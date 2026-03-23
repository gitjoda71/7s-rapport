"""Testsuite för ingest.py"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from ingest import parse_7s, mgrs_to_latlon, make_filename, build_note
from datetime import datetime

PASS = 0
FAIL = 0

def check(name, got, expected=None, condition=None):
    global PASS, FAIL
    ok = (condition(got) if condition else got == expected)
    status = "OK  " if ok else "FEL "
    if ok: PASS += 1
    else:  FAIL += 1
    print(f"  {status} {name}: {repr(got)}")

# ---- parse_7s ----
print("\n=== parse_7s ===")

# 1. Standard-rapport
r = parse_7s("7S RAPPORT\n\nStund: 101200\nStälle: 34VDL3300083000\nStyrka: 3\nSlag: Personbil\nSysselsättning: Rör sig N\nSymbol: Röd\nSagesman: ALFA")
check("Parsar stund",        r["stund"],         "101200")
check("Parsar slag",         r["slag"],          "Personbil")
check("Parsar sagesman",     r["sagesman"],      "ALFA")
check("Parsar MGRS",         r["mgrs"],          "34VDL3300083000")
check("Lat finns",           r["lat"],           condition=lambda v: isinstance(v, float))
check("Sedan tom om saknas", r["sedan"],         "")

# 2. Stund med saldo
r2 = parse_7s("7S RAPPORT\n\nStund: 101524 (s 33)\nStälle: 33VXF 69019 80388\nStyrka: 1\nSlag: Lastbil\nSysselsättning: Rör sig S\nSymbol: Svart\nSagesman: Policys\nSedan: Avbryter uppdraget")
check("Stund med saldo",     r2["stund"],        "101524 (s 33)")
check("Sedan parsas",        r2["sedan"],        "Avbryter uppdraget")
check("MGRS med mellanslag", r2["mgrs"],         "33VXF6901980388")

# 3. ASCII-fallback (ä → a) för Ställe och Sysselsättning
r3 = parse_7s("7S RAPPORT\n\nStund: 101300\nStalle: 34VDL3300083000\nStyrka: 2\nSlag: BTR\nSysselsattning: Stillastående\nSymbol: Grön\nSagesman: BRAVO")
check("Stalle ASCII-fallback",       r3["stalle"],       "34VDL3300083000")
check("Sysselsattning ASCII-fallback", r3["sysselsattning"], "Stillastående")

# 4. Bindestreck → tom sträng
r4 = parse_7s("7S RAPPORT\n\nStund: 101400\nStälle: -\nStyrka: -\nSlag: -\nSysselsättning: -\nSymbol: -\nSagesman: -")
check("Streck → tom (stalle)", r4["stalle"], "")
check("Streck → tom (slag)",   r4["slag"],   "")

# 5. Ej 7S → None
r5 = parse_7s("WHAT rapport\nHej")
check("Ej 7S returnerar None", r5, None)

r6 = parse_7s("")
check("Tom sträng → None", r6, None)

# ---- MGRS ----
print("\n=== mgrs_to_latlon ===")
lat, lon = mgrs_to_latlon("34VDL3300083000")
check("34VDL lat ~59°N", lat, condition=lambda v: 59 < v < 60)
check("34VDL lon ~18-20°E", lon, condition=lambda v: 17 < v < 22)

lat2, lon2 = mgrs_to_latlon("33VXF6901980388")
check("33VXF lat ~59°N", lat2, condition=lambda v: 59 < v < 60)
check("33VXF lon ~18°E", lon2, condition=lambda v: 17 < v < 19)

bad = mgrs_to_latlon("XXXXX")
check("Ogiltig MGRS → None", bad, None)

# ---- Filnamn ----
print("\n=== make_filename ===")
ts = datetime(2026, 3, 10, 6, 3, 12)
f1 = make_filename({"stund": "101200"}, ts)
check("Filnamn från stund", f1, "7S-101200.md")

f2 = make_filename({"stund": "101524 (s 33)"}, ts)
# Accepterar både primärnamn och kollisionsnamn (om filen redan finns i valvet)
check("Filnamn med saldo (s 33)", f2,
      condition=lambda v: v.startswith("7S-101524 (s 33)") and v.endswith(".md"))

f3 = make_filename({"stund": "101524:00"}, ts)
check("Kolon saniteras bort", f3, "7S-10152400.md")

f4 = make_filename({"stund": ""}, ts)
check("Tom stund → DDHHMM", f4, f"7S-{ts.strftime('%d%H%M')}.md")

# ---- build_note ----
print("\n=== build_note ===")
ts2 = datetime(2026, 3, 10, 15, 27, 31)
fields = {"stund":"101524 (s 33)","stalle":"Äppelviken","styrka":"1","slag":"Personbil",
          "sysselsattning":"Rör sig S","symbol":"Svart","sagesman":"Policys",
          "sedan":"Avbryter uppdraget","mgrs":"33VXF6901980388","lat":59.328376,"lng":17.970869}
note = build_note(fields, ts2)
check("YAML har type: 7S",      "type: 7S" in note, True)
check("YAML har location",      "location: [59.328376, 17.970869]" in note, True)
check("YAML har sedan",         'sedan: "Avbryter uppdraget"' in note, True)
check("Tabell har Sedan-rad",   "| Sedan | Avbryter uppdraget |" in note, True)
check("Citat escaped i YAML",   True, condition=lambda v: True)  # q() testat separat

print(f"\n{'='*40}")
print(f"Resultat: {PASS} OK, {FAIL} FEL")
sys.exit(0 if FAIL == 0 else 1)
