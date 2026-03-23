"""
mock_sender.py – Skicka testrapporter till ingest.py utan Signal
================================================================
Genererar exakt samma textsträng som PWA:ns generateReport()-funktion.
Se FORMAT.md för specifikation.

Användning:
    python mock_sender.py              # skickar en slumpmässig rapport
    python mock_sender.py --antal 5    # skickar 5 rapporter med 2s mellanrum
    python mock_sender.py --fast       # skickar utan paus
"""

import argparse
import random
import requests
import time
from datetime import datetime

WEBHOOK_URL = "http://localhost:8000/webhook"

# Testdata
SAGESMAN_POOL = [
    "NIN 111. 1a p, 2 grp. Nils Nilsson",
    "NIN 112. 1a p, 3 grp. Erik Eriksson",
    "NIN 121. 2a p, 1 grp. Anna Andersson",
    "NIN 211. 3a p, 1 grp. Lars Larsson",
]

MGRS_POOL = [
    "34VDL3300083000",  # T-Centralen / Sveavägen
    "34VDL3380082200",  # Gamla Stan, Skeppsbron
    "34VDL3560084000",  # Östermalm, Karlaplan
    "34VDL3180083100",  # Kungsholmen, Rådhuset
    "34VDL3370081500",  # Södermalm, Slussen
    "34VDL3270083800",  # Norrmalm, Hötorget
]

SLAG_POOL = [
    "Fientlig BTR, pansarskyddad",
    "Infanteri till fots",
    "Lastbil, militär",
    "Stridsvagn, T-72-typ",
    "Beväpnade civilister",
]

SYSSELSATTNING_POOL = [
    "Rör sig norrut längs väg",
    "Grupperar i skogsdungen",
    "Håller eld mot vår position",
    "Stillastående, verkar rekognosera",
    "Gräver ned, möjlig positionering",
]

SYMBOL_POOL = [
    "Grön, inga synliga märkningar",
    "Kamouflage, röd arm-bricka",
    "Mörkgrå, Z-märkning på sidan",
    "Olivgrön, okänt förbandstecken",
]


def make_stund() -> str:
    now = datetime.now()
    return f"{now.day:02d}{now.hour:02d}{now.minute:02d}"


def make_rapport(mgrs: str | None = None) -> str:
    """Genererar exakt samma sträng som PWA:ns generateReport()."""
    stund         = make_stund()
    stalle        = mgrs or random.choice(MGRS_POOL)
    styrka        = str(random.randint(1, 12))
    slag          = random.choice(SLAG_POOL)
    sysselsattning = random.choice(SYSSELSATTNING_POOL)
    symbol        = random.choice(SYMBOL_POOL)
    sagesman      = random.choice(SAGESMAN_POOL)

    # OBS: matchar exakt generateReport() i index.html
    report  = "7S RAPPORT\n\n"
    report += f"Stund: {stund}\n"
    report += f"Ställe: {stalle}\n"
    report += f"Styrka: {styrka}\n"
    report += f"Slag: {slag}\n"
    report += f"Sysselsättning: {sysselsattning}\n"
    report += f"Symbol: {symbol}\n"
    report += f"Sagesman: {sagesman}"   # ingen \n i slutet – exakt som PWA:n

    return report


def send(rapport: str, sender: str = "+46700000001"):
    payload = {
        "envelope": {
            "source": sender,
            "dataMessage": {"message": rapport}
        }
    }
    try:
        r = requests.post(WEBHOOK_URL, json=payload, timeout=5)
        r.raise_for_status()
        print(f"  -> {r.json()}")
    except Exception as e:
        print(f"  -> FEL: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Skicka mock 7S-rapporter")
    parser.add_argument("--antal", type=int, default=1,  help="Antal rapporter att skicka")
    parser.add_argument("--fast",  action="store_true",  help="Ingen paus mellan rapporter")
    args = parser.parse_args()

    for i in range(args.antal):
        rapport = make_rapport()
        print(f"\n[{i+1}/{args.antal}] Skickar:\n{rapport}\n")
        send(rapport)
        if not args.fast and i < args.antal - 1:
            time.sleep(2)

    print("\nKlart.")
