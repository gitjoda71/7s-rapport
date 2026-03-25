"""
M-blankett PDF-generator

Parsar råtext med militära fältformat (TILL:, FRÅN:, TID:, ÄMNE:, SIGN:)
och genererar en formaterad M-blankett som PDF.

Kan köras fristående för test:
    python m_blankett_pdf.py [indata.txt] [utdata.pdf]
"""

import re
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from fpdf import FPDF

# ---------------------------------------------------------------------------
#  Parser
# ---------------------------------------------------------------------------

# Fältmönster (case-insensitive, multiline)
FIELD_PATTERNS = {
    "till": re.compile(r"^TILL:\s*(.+)$", re.MULTILINE | re.IGNORECASE),
    "fran": re.compile(r"^FR[ÅA]N:\s*(.+)$", re.MULTILINE | re.IGNORECASE),
    "tid": re.compile(r"^TID:\s*(.+)$", re.MULTILINE | re.IGNORECASE),
    "amne": re.compile(r"^(?:ÄMNE|AMNE|RUBRIK):\s*(.+)$", re.MULTILINE | re.IGNORECASE),
    "sign": re.compile(r"^(?:SIGN|AVS SIGN|UNDERSKRIFT):\s*(.+)$", re.MULTILINE | re.IGNORECASE),
}

HEADER_FIELD_RE = re.compile(
    r"^(?:TILL|FRÅN|FRAN|TID|ÄMNE|AMNE|RUBRIK|SIGN|AVS SIGN|UNDERSKRIFT):",
    re.MULTILINE | re.IGNORECASE,
)


def generate_tnr(timestamp: datetime | None = None) -> str:
    """Generera TNR (tidnummerreferens) från tidstämpel, t.ex. 251400AMAR2026."""
    ts = timestamp or datetime.now(timezone.utc)
    month_names = {
        1: "JAN", 2: "FEB", 3: "MAR", 4: "APR", 5: "MAJ", 6: "JUN",
        7: "JUL", 8: "AUG", 9: "SEP", 10: "OKT", 11: "NOV", 12: "DEC",
    }
    return f"{ts.day:02d}{ts.hour:02d}{ts.minute:02d}A{month_names[ts.month]}{ts.year}"


def parse_message(raw_text: str, timestamp: datetime | None = None) -> dict:
    """
    Parsa råtext till ett dict med fälten:
        till, fran, tid, amne, sign, body, tnr
    """
    # Normalisera radbrytningar
    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")

    # Separera header och body
    header, body = _split_header_body(text)

    # Extrahera fält från headern
    data = {}
    for key, pattern in FIELD_PATTERNS.items():
        m = pattern.search(header)
        data[key] = m.group(1).strip() if m else ""

    # SIGN kan ligga i slutet av body
    if not data["sign"]:
        sign_match = list(FIELD_PATTERNS["sign"].finditer(body))
        if sign_match:
            data["sign"] = sign_match[-1].group(1).strip()
            # Ta bort sign-raden från body
            body = body[: sign_match[-1].start()] + body[sign_match[-1].end() :]

    data["body"] = body.strip()

    # TNR: generera om TID saknas
    data["tnr"] = data.get("tid") or generate_tnr(timestamp)

    return data


def _split_header_body(text: str) -> tuple[str, str]:
    """Separera header från body via --- eller dubbel radbrytning."""
    # Primär: ---
    parts = re.split(r"\n-{3,}\n?", text, maxsplit=1)
    if len(parts) == 2:
        return parts[0], parts[1]

    # Fallback: dubbel radbrytning om headerfält finns
    pos = text.find("\n\n")
    if pos > 0 and HEADER_FIELD_RE.search(text[:pos]):
        return text[:pos], text[pos + 2 :]

    # Ingen struktur — allt är body
    return "", text


# ---------------------------------------------------------------------------
#  PDF-generator
# ---------------------------------------------------------------------------

# Layout-konstanter (mm)
MARGIN_LEFT = 25
MARGIN_TOP = 20
MARGIN_RIGHT = 25
PAGE_WIDTH = 210  # A4
CONTENT_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT

# Kolumnpositioner (mm från vänster marginal)
COL2_X = 70   # FRÅN
COL3_X = 130  # TID

LABEL_SIZE = 8
VALUE_SIZE = 11
BODY_SIZE = 11
BODY_INDENT = 5  # mm

LABEL_COLOR = (80, 80, 80)
BLACK = (0, 0, 0)


def _get_font_path() -> str | None:
    """Hitta en inbäddad font i fonts/-mappen, eller None för inbyggd."""
    fonts_dir = Path(__file__).parent / "fonts"
    for name in ["LiberationSans-Regular.ttf", "Arial.ttf", "Helvetica.ttf"]:
        path = fonts_dir / name
        if path.exists():
            return str(path)
    return None


class MBlankettPDF(FPDF):
    """PDF-dokument formaterat som M-blankett."""

    def __init__(self):
        super().__init__(format="A4")
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT)

        # Försök ladda extern font, annars inbyggd Helvetica
        font_path = _get_font_path()
        if font_path:
            self.add_font("MFont", "", font_path, uni=True)
            bold_path = font_path.replace("Regular", "Bold")
            if os.path.exists(bold_path):
                self.add_font("MFont", "B", bold_path, uni=True)
            else:
                self.add_font("MFont", "B", font_path, uni=True)
            self._font_family = "MFont"
        else:
            self._font_family = "Helvetica"

    def _use_font(self, style: str = "", size: int = 11):
        self.set_font(self._font_family, style, size)


def generate_pdf(data: dict, output_path: str) -> str:
    """
    Generera en M-blankett PDF.

    Args:
        data: dict från parse_message()
        output_path: sökväg till PDF-filen

    Returns:
        Sökvägen till skapad PDF
    """
    pdf = MBlankettPDF()
    pdf.add_page()

    # --- Rad 1: Etiketter (TILL / FRÅN / TID) ---
    pdf.set_text_color(*LABEL_COLOR)
    pdf._use_font(size=LABEL_SIZE)

    y = pdf.get_y()
    pdf.set_xy(MARGIN_LEFT, y)
    pdf.cell(w=COL2_X - MARGIN_LEFT, h=4, text="TILL", new_x="LEFT", new_y="TOP")
    pdf.set_xy(COL2_X, y)
    pdf.cell(w=COL3_X - COL2_X, h=4, text="FRÅN", new_x="LEFT", new_y="TOP")
    pdf.set_xy(COL3_X, y)
    pdf.cell(w=0, h=4, text="TID", new_x="LMARGIN", new_y="NEXT")

    # --- Rad 2: Värden ---
    pdf.set_text_color(*BLACK)
    pdf._use_font(size=VALUE_SIZE)

    y = pdf.get_y()
    till_val = data.get("till") or "-"
    fran_val = data.get("fran") or "-"
    tid_val = data.get("tid") or "-"

    pdf.set_xy(MARGIN_LEFT, y)
    pdf.cell(w=COL2_X - MARGIN_LEFT, h=6, text=till_val, new_x="LEFT", new_y="TOP")
    pdf.set_xy(COL2_X, y)
    pdf.cell(w=COL3_X - COL2_X, h=6, text=fran_val, new_x="LEFT", new_y="TOP")
    pdf.set_xy(COL3_X, y)
    pdf.cell(w=0, h=6, text=tid_val, new_x="LMARGIN", new_y="NEXT")

    pdf.ln(2)

    # --- Rad 3: Etikett ÄMNE ---
    pdf.set_text_color(*LABEL_COLOR)
    pdf._use_font(size=LABEL_SIZE)
    pdf.cell(w=0, h=4, text="ÄMNE", new_x="LMARGIN", new_y="NEXT")

    # --- Rad 4: Ämne-värde (fetstil) ---
    pdf.set_text_color(*BLACK)
    pdf._use_font(style="B", size=VALUE_SIZE)
    amne_val = data.get("amne") or "-"
    pdf.cell(w=0, h=6, text=amne_val, new_x="LMARGIN", new_y="NEXT")

    pdf.ln(2)

    # --- Avdelare ---
    y = pdf.get_y()
    pdf.set_draw_color(*BLACK)
    pdf.set_line_width(0.5)
    pdf.line(MARGIN_LEFT, y, PAGE_WIDTH - MARGIN_RIGHT, y)

    pdf.ln(4)

    # --- Brödtext ---
    pdf._use_font(size=BODY_SIZE)
    pdf.set_text_color(*BLACK)

    body = data.get("body", "")
    if body:
        # Indrag för brödtext
        pdf.set_x(MARGIN_LEFT + BODY_INDENT)
        pdf.multi_cell(
            w=CONTENT_WIDTH - BODY_INDENT,
            h=6,
            text=body,
            new_x="LMARGIN",
            new_y="NEXT",
        )

    # --- Signatur ---
    sign = data.get("sign", "")
    if sign:
        pdf.ln(10)
        pdf._use_font(size=BODY_SIZE)
        pdf.set_x(MARGIN_LEFT + BODY_INDENT)
        pdf.cell(w=0, h=6, text=sign)

    # Spara
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    pdf.output(output_path)
    return output_path


# ---------------------------------------------------------------------------
#  CLI: kör fristående för test
# ---------------------------------------------------------------------------

def main():
    """Kör fristående: python m_blankett_pdf.py [indata.txt] [utdata.pdf]"""
    # Standardvärden
    tests_dir = Path(__file__).parent.parent / "tests"
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    if len(sys.argv) >= 2:
        # Specifik fil angiven
        input_files = [Path(sys.argv[1])]
        if len(sys.argv) >= 3:
            output_files = [Path(sys.argv[2])]
        else:
            output_files = [output_dir / input_files[0].with_suffix(".pdf").name]
    else:
        # Kör alla testfiler
        input_files = sorted(tests_dir.glob("*.txt"))
        output_files = [output_dir / f.with_suffix(".pdf").name for f in input_files]

    if not input_files:
        print("Inga testfiler hittade. Ange en fil som argument.")
        sys.exit(1)

    for infile, outfile in zip(input_files, output_files):
        print(f"Läser: {infile}")
        raw_text = infile.read_text(encoding="utf-8")
        data = parse_message(raw_text)

        print(f"  TILL: {data['till'] or '(saknas)'}")
        print(f"  FRÅN: {data['fran'] or '(saknas)'}")
        print(f"  TID:  {data['tid'] or '(saknas)'}")
        print(f"  ÄMNE: {data['amne'] or '(saknas)'}")
        print(f"  SIGN: {data['sign'] or '(saknas)'}")
        print(f"  Body: {len(data['body'])} tecken")

        generate_pdf(data, str(outfile))
        print(f"  -> PDF: {outfile}")
        print()

    print("Klart!")


if __name__ == "__main__":
    main()
