"""
ingest.py – Signal-webhook → Obsidian-not
==========================================
Tar emot webhook från signal-cli-rest-api, parsar 7S-rapporter
och skapar markdown-noter i Obsidian-valvet via Local REST API-pluginet.

Starta med:
    uvicorn ingest:app --host 0.0.0.0 --port 8000

Kräver:
    pip install fastapi uvicorn requests mgrs python-dotenv
"""

import re
import os
import json
import asyncio
import mgrs as mgrs_lib
import requests
import urllib3
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

# --- Konfiguration (.env eller miljövariabler) ---
VAULT_API   = os.getenv("OBSIDIAN_API",   "https://localhost:27124")
API_TOKEN   = os.getenv("OBSIDIAN_TOKEN", "byt-ut-mig")
RAPPORT_DIR = os.getenv("RAPPORT_DIR",    "Stabssystem/Rapporter")
SIGNAL_API      = os.getenv("SIGNAL_API",      "http://localhost:8080")
SIGNAL_NUM      = os.getenv("SIGNAL_NUM",      "+46722080939")
SIGNAL_GROUP_ID = os.getenv("SIGNAL_GROUP_ID", "")
POLL_SEC    = int(os.getenv("POLL_SEC",   "5"))
DEBUG_LOG   = os.getenv("DEBUG_LOG",      "poll_debug.log")

RAW_LOG = f"{RAPPORT_DIR}/raw_signals.log"

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "text/markdown; charset=utf-8",
}

m = mgrs_lib.MGRS()

# --- Regex mot exakt PWA-format (se FORMAT.md) ---

FIELD_RE = {
    "stund":          re.compile(r"^Stund:\s*(.+)$",          re.MULTILINE),
    "stalle":         re.compile(r"^St(?:ä|a)lle:\s*(.+)$",   re.MULTILINE | re.IGNORECASE),
    "styrka":         re.compile(r"^Styrka:\s*(.+)$",         re.MULTILINE),
    "slag":           re.compile(r"^Slag:\s*(.+)$",           re.MULTILINE),
    "sysselsattning": re.compile(r"^Syssels(?:ä|a)ttning:\s*(.+)$", re.MULTILINE | re.IGNORECASE),
    "symbol":         re.compile(r"^Symbol:\s*(.+)$",         re.MULTILINE),
    "sagesman":       re.compile(r"^Sagesman:\s*(.+)$",       re.MULTILINE),
    "sedan":          re.compile(r"^Sedan:\s*(.+)$",          re.MULTILINE),
}

# MGRS: 2 siffror + 3 bokstäver + 10 siffror (med eller utan mellanslag)
MGRS_RE = re.compile(r"\b(\d{2}[A-Z]{3}\s?\d{5}\s?\d{5}|\d{2}[A-Z]{3}\d{10})\b")

# Ogiltiga tecken i Windows-filnamn
UNSAFE_FILENAME = re.compile(r'[\\/:*?"<>|]')


def extract(pattern, text: str) -> str:
    match = pattern.search(text)
    val = match.group(1).strip() if match else ""
    return "" if val == "-" else val


def mgrs_to_latlon(mgrs_str: str) -> tuple[float, float] | None:
    clean = mgrs_str.replace(" ", "")
    try:
        lat, lon = m.toLatLon(clean.encode())
        return round(float(lat), 6), round(float(lon), 6)
    except Exception:
        return None


def parse_7s(text: str) -> dict | None:
    fields = {key: extract(pat, text) for key, pat in FIELD_RE.items()}

    # Kräv minst Stund + Ställe, annars är det inte en 7S-rapport
    if not fields["stund"] or not fields["stalle"]:
        return None

    # Hitta MGRS i Ställe-fältet, fallback: sök hela texten
    mgrs_match = MGRS_RE.search(fields["stalle"]) or MGRS_RE.search(text)

    latlon = None
    mgrs_str = ""
    if mgrs_match:
        mgrs_str = mgrs_match.group(1).replace(" ", "")
        latlon = mgrs_to_latlon(mgrs_str)

    fields["mgrs"] = mgrs_str
    fields["lat"]  = latlon[0] if latlon else ""
    fields["lng"]  = latlon[1] if latlon else ""

    return fields


def build_note(fields: dict, ts: datetime) -> str:
    ts_str = ts.strftime("%Y-%m-%dT%H:%M:%S")

    location_str = (
        f"[{fields['lat']}, {fields['lng']}]" if fields["lat"] != "" else ""
    )

    def q(s):
        return str(s).replace('"', '\\"')

    sedan = fields.get("sedan", "")

    return f"""---
type: 7S
timestamp: {ts_str}
sagesman: "{q(fields['sagesman'])}"
location: {location_str}
mgrs: {fields['mgrs']}
stund: "{q(fields['stund'])}"
stalle: "{q(fields['stalle'])}"
styrka: "{q(fields['styrka'])}"
slag: "{q(fields['slag'])}"
sysselsattning: "{q(fields['sysselsattning'])}"
symbol: "{q(fields['symbol'])}"
sedan: "{q(sedan)}"
---

**Sagesman:** {fields['sagesman']}
**Stund:** {fields['stund']}  |  **Inkom:** {ts.strftime('%H:%M:%S')}

| Fält | Värde |
|---|---|
| Ställe | {fields['stalle']} |
| MGRS | {fields['mgrs']} |
| Styrka | {fields['styrka']} |
| Slag | {fields['slag']} |
| Sysselsättning | {fields['sysselsattning']} |
| Symbol | {fields['symbol']} |
| Sedan | {sedan} |
"""


def make_filename(fields: dict, ts: datetime) -> str:
    """Genererar filnamn från stund-fältet. Lägger till sekunder vid krock."""
    stund = fields.get("stund", "").strip() or ts.strftime("%d%H%M")
    safe = UNSAFE_FILENAME.sub("", stund)
    base = safe
    candidate = f"{base}.md"
    # Kolla om filen redan finns via Obsidian API
    url = f"{VAULT_API}/vault/{RAPPORT_DIR}/{candidate}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=3, verify=False)
        if resp.status_code == 200:
            # Krock — lägg till HH:MM:SS
            candidate = f"{base}-{ts.strftime('%H%M%S')}.md"
    except Exception:
        pass
    return candidate


def write_note(filename: str, content: str):
    url = f"{VAULT_API}/vault/{RAPPORT_DIR}/{filename}"
    resp = requests.put(
        url, headers=HEADERS, data=content.encode("utf-8"), timeout=5, verify=False
    )
    resp.raise_for_status()


MASTERKARTA_PATH = os.getenv("MASTERKARTA_PATH", "Stabssystem/Masterkarta.md")
TOUCH_RE = re.compile(r"<!-- lastUpdate: .* -->")

def touch_masterkarta():
    """Uppdaterar tidsstämpeln i Masterkarta.md så Obsidian renderar om kartan."""
    url = f"{VAULT_API}/vault/{MASTERKARTA_PATH}"
    try:
        r = requests.get(url, headers=_get_headers, timeout=5, verify=False)
        if not r.ok:
            return
        ts = datetime.now().isoformat(timespec="seconds")
        updated = TOUCH_RE.sub(f"<!-- lastUpdate: {ts} -->", r.text)
        requests.put(url, headers=HEADERS, data=updated.encode("utf-8"), timeout=5, verify=False)
    except Exception as e:
        print(f"[TOUCH] FEL: {e}", flush=True)


def append_raw_log(sender: str, raw: str):
    ts = datetime.now().isoformat(timespec="seconds")
    entry = f"\n---\n**{ts}** | Från: `{sender}`\n```\n{raw}\n```\n"
    url = f"{VAULT_API}/vault/{RAW_LOG}"
    try:
        existing = requests.get(url, headers=HEADERS, timeout=5, verify=False).text
    except Exception:
        existing = "# Rådata-logg\n\nOkända eller icke-parsade meddelanden.\n"
    requests.put(
        url, headers=HEADERS,
        data=(existing + entry).encode("utf-8"),
        timeout=5, verify=False
    )


def process_envelope(body: dict) -> dict:
    """Extraherar text och avsändare ur ett Signal-envelope och skapar Obsidian-not."""
    env = body.get("envelope", {})
    sender = env.get("source", "unknown")

    data_msg = env.get("dataMessage") or {}
    text = data_msg.get("message")

    # Note to Self / sync-meddelande (skickat från egna enheten)
    if not text:
        sent = (env.get("syncMessage") or {}).get("sentMessage") or {}
        data_msg = sent
        text = sent.get("message")

    if not text:
        return {"status": "ignored", "reason": "no_text"}

    # Filtrera på grupp om SIGNAL_GROUP_ID är satt
    if SIGNAL_GROUP_ID:
        group_id = (data_msg.get("groupInfo") or {}).get("groupId", "")
        if group_id != SIGNAL_GROUP_ID:
            return {"status": "ignored", "reason": "wrong_group"}

    fields = parse_7s(text)
    if not fields:
        append_raw_log(sender, text)
        return {"status": "logged_raw"}

    ts = datetime.now()
    filename = make_filename(fields, ts)
    note = build_note(fields, ts)
    write_note(filename, note)
    touch_masterkarta()
    return {"status": "ok", "file": filename}


# --- Polling ---

async def poll_signal():
    """Hämtar inkommande Signal-meddelanden var POLL_SEC sekund."""
    while True:
        try:
            url = f"{SIGNAL_API}/v1/receive/{SIGNAL_NUM}"
            resp = requests.get(url, timeout=10)
            if resp.ok:
                msgs = resp.json()
                if msgs:
                    print(f"[POLL] {len(msgs)} meddelanden", flush=True)
                for env in msgs:
                    if DEBUG_LOG:
                        with open(DEBUG_LOG, "a", encoding="utf-8") as f:
                            f.write(json.dumps(env, ensure_ascii=False) + "\n")
                    result = process_envelope(env)
                    print(f"[POLL] -> {result}", flush=True)
        except Exception as e:
            print(f"[POLL] FEL: {e}", flush=True)
        await asyncio.sleep(POLL_SEC)


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(poll_signal())
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# --- YAML-parser för noter ---

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
YAML_LINE_RE   = re.compile(r"^(\w+):\s*(.+)$", re.MULTILINE)
LOCATION_RE    = re.compile(r"\[\s*([+-]?\d+\.?\d*)\s*,\s*([+-]?\d+\.?\d*)\s*\]")

_get_headers = {"Authorization": f"Bearer {API_TOKEN}"}

def parse_note_yaml(content: str) -> dict | None:
    fm = FRONTMATTER_RE.match(content)
    if not fm:
        return None
    fields: dict = {}
    for match in YAML_LINE_RE.finditer(fm.group(1)):
        key = match.group(1)
        val = match.group(2).strip().strip('"')
        fields[key] = val
    if fields.get("type") != "7S":
        return None
    loc = LOCATION_RE.search(fields.get("location", ""))
    if not loc:
        return None
    fields["lat"] = float(loc.group(1))
    fields["lng"] = float(loc.group(2))
    return fields


# --- Endpoints ---

@app.post("/webhook")
async def webhook(req: Request):
    """Tar emot webhook från signal-cli-rest-api."""
    body = await req.json()
    return process_envelope(body)


@app.get("/health")
def health():
    return {"status": "up", "time": datetime.now().isoformat(timespec="seconds")}


@app.get("/reports")
def get_reports():
    """Returnerar alla 7S-rapporter från Obsidian-valvet som JSON."""
    try:
        url = f"{VAULT_API}/vault/{RAPPORT_DIR}/"
        resp = requests.get(url, headers=_get_headers, timeout=5, verify=False)
        resp.raise_for_status()
        files = [
            f.split("/")[-1] for f in resp.json().get("files", [])
            if f.endswith(".md") and "raw_signals" not in f
        ]
    except Exception as e:
        return {"error": str(e), "reports": []}

    reports = []
    for filename in files:
        try:
            url = f"{VAULT_API}/vault/{RAPPORT_DIR}/{filename}"
            r = requests.get(url, headers=_get_headers, timeout=5, verify=False)
            fields = parse_note_yaml(r.text)
            if not fields:
                continue
            reports.append({
                "id":             filename.replace(".md", ""),
                "stund":          fields.get("stund", ""),
                "stalle":         fields.get("stalle", ""),
                "styrka":         fields.get("styrka", ""),
                "slag":           fields.get("slag", ""),
                "sysselsattning": fields.get("sysselsattning", ""),
                "symbol":         fields.get("symbol", ""),
                "sagesman":       fields.get("sagesman", ""),
                "sedan":          fields.get("sedan", ""),
                "timestamp":      fields.get("timestamp", ""),
                "lat":            fields["lat"],
                "lng":            fields["lng"],
                "mgrs":           fields.get("mgrs", ""),
            })
        except Exception:
            continue

    return {"reports": reports}
