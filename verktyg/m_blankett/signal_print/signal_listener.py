"""
Signal webhook-mottagare för M-blankett.

Tar emot meddelanden från signal-cli-rest-api via webhook (POST),
parsar dem, genererar PDF och skickar till skrivaren.
"""

import os
import logging
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Request

from m_blankett_pdf import parse_message, generate_pdf
from printer import print_pdf

logger = logging.getLogger("m_blankett")

app = FastAPI(title="M-blankett Signal Listener")

# Konfiguration (sätts av main.py vid start)
SIGNAL_GROUP_ID: str = ""
PRINTER_NAME: str = "default"
PRINTER_METHOD: str = "auto"
OUTPUT_DIR: str = "./output"
AUTO_PRINT: bool = True


def configure(
    group_id: str,
    printer_name: str = "default",
    printer_method: str = "auto",
    output_dir: str = "./output",
    auto_print: bool = True,
):
    """Sätt konfiguration (anropas från main.py)."""
    global SIGNAL_GROUP_ID, PRINTER_NAME, PRINTER_METHOD, OUTPUT_DIR, AUTO_PRINT
    SIGNAL_GROUP_ID = group_id
    PRINTER_NAME = printer_name
    PRINTER_METHOD = printer_method
    OUTPUT_DIR = output_dir
    AUTO_PRINT = auto_print


@app.post("/api/v1/webhook")
async def webhook(request: Request):
    """
    Tar emot webhook från signal-cli-rest-api.

    Förväntat JSON-format:
    {
        "envelope": {
            "dataMessage": {
                "message": "TILL: ...\nFRÅN: ...\n---\nBrödtext",
                "timestamp": 1711360000000,
                "groupInfo": {
                    "groupId": "grupp-id"
                }
            },
            "sourceName": "Avsändare",
            "sourceNumber": "+46..."
        }
    }
    """
    try:
        body = await request.json()
    except Exception:
        logger.warning("Ogiltigt JSON i webhook")
        return {"status": "error", "detail": "Ogiltigt JSON"}

    envelope = body.get("envelope", {})
    data_msg = envelope.get("dataMessage")

    if not data_msg:
        # Inte ett datameddelande (kvitto, typing-indikator etc.)
        return {"status": "ignored", "detail": "Inget dataMessage"}

    # Filtrera på grupp
    group_info = data_msg.get("groupInfo", {})
    group_id = group_info.get("groupId", "")

    if SIGNAL_GROUP_ID and group_id != SIGNAL_GROUP_ID:
        logger.debug(f"Ignorerar meddelande från annan grupp: {group_id}")
        return {"status": "ignored", "detail": "Annan grupp"}

    # Extrahera meddelande
    message_text = data_msg.get("message", "")
    if not message_text or not message_text.strip():
        return {"status": "ignored", "detail": "Tomt meddelande"}

    # Tidstämpel (signal-cli ger millisekunder)
    ts_ms = data_msg.get("timestamp", 0)
    timestamp = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc) if ts_ms else None

    source_name = envelope.get("sourceName", "")
    logger.info(f"Nytt meddelande från {source_name} i grupp {group_id}")

    # Parsa och generera PDF
    parsed = parse_message(message_text, timestamp=timestamp)

    # Filnamn baserat på TNR
    tnr = parsed.get("tnr", datetime.now().strftime("%Y%m%d_%H%M%S"))
    safe_tnr = tnr.replace("/", "-").replace("\\", "-").replace(" ", "_")
    pdf_filename = f"M_{safe_tnr}.pdf"
    pdf_path = os.path.join(OUTPUT_DIR, pdf_filename)

    generate_pdf(parsed, pdf_path)
    logger.info(f"PDF genererad: {pdf_path}")

    # Skriv ut
    printed = False
    if AUTO_PRINT:
        printed = print_pdf(pdf_path, printer_name=PRINTER_NAME, method=PRINTER_METHOD)
        if printed:
            logger.info(f"Utskriven: {pdf_path}")
        else:
            logger.warning(f"Utskrift misslyckades: {pdf_path}")

    return {
        "status": "ok",
        "pdf": pdf_path,
        "printed": printed,
        "till": parsed.get("till", ""),
        "amne": parsed.get("amne", ""),
        "tnr": tnr,
    }


@app.get("/health")
async def health():
    """Hälsokontroll."""
    return {"status": "ok", "group_id": SIGNAL_GROUP_ID}
