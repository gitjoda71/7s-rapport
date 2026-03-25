"""
M-blankett Signal → PDF → Skrivare

Startpunkt: laddar konfiguration och startar webhook-servern.

Användning:
    python main.py
"""

import os
import sys
import logging
from pathlib import Path

from dotenv import load_dotenv
import uvicorn

from signal_listener import app, configure

# Konfigurera loggning
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("m_blankett")


def main():
    # Ladda .env
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"Konfiguration laddad från {env_path}")
    else:
        logger.warning(
            f".env saknas ({env_path}). "
            "Kopiera config.example.env till .env och fyll i."
        )

    # Läs konfiguration
    group_id = os.getenv("SIGNAL_GROUP_ID", "")
    printer_name = os.getenv("PRINTER_NAME", "default")
    printer_method = os.getenv("PRINTER_METHOD", "auto")
    output_dir = os.getenv("OUTPUT_DIR", "./output")
    port = int(os.getenv("PORT", "8080"))
    auto_print = os.getenv("AUTO_PRINT", "true").lower() in ("true", "1", "yes")

    # Skapa output-mapp
    os.makedirs(output_dir, exist_ok=True)

    # Konfigurera lyssnaren
    configure(
        group_id=group_id,
        printer_name=printer_name,
        printer_method=printer_method,
        output_dir=output_dir,
        auto_print=auto_print,
    )

    if not group_id:
        logger.warning(
            "SIGNAL_GROUP_ID ej satt — alla meddelanden från alla grupper tas emot!"
        )

    logger.info(f"Startar M-blankett webhook-server på port {port}")
    logger.info(f"  Grupp-ID:  {group_id or '(alla)'}")
    logger.info(f"  Skrivare:  {printer_name}")
    logger.info(f"  Metod:     {printer_method}")
    logger.info(f"  Output:    {output_dir}")
    logger.info(f"  Autoprint: {auto_print}")
    logger.info("")
    logger.info("Konfigurera signal-cli-rest-api webhook till:")
    logger.info(f"  http://<denna-dator>:{port}/api/v1/webhook")

    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
