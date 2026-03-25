"""
Utskriftsmodul för M-blankett PDF.

Stödjer Windows, Mac och Linux.
Kan köras fristående för test:
    python printer.py fil.pdf [skrivarnamn]
"""

import os
import sys
import shutil
import subprocess
import platform


def print_pdf(pdf_path: str, printer_name: str = "default", method: str = "auto") -> bool:
    """
    Skriv ut en PDF-fil.

    Args:
        pdf_path: Sökväg till PDF
        printer_name: Skrivarnamn eller "default"
        method: "auto", "lp", "sumatrapdf", "osprint"

    Returns:
        True om utskrift lyckades
    """
    if not os.path.exists(pdf_path):
        print(f"[printer] Filen finns inte: {pdf_path}")
        return False

    system = platform.system()

    if method == "auto":
        method = _detect_method(system)

    try:
        if method == "lp":
            return _print_lp(pdf_path, printer_name)
        elif method == "sumatrapdf":
            return _print_sumatrapdf(pdf_path, printer_name)
        elif method == "osprint":
            return _print_os(pdf_path)
        else:
            print(f"[printer] Okänd metod: {method}")
            return False
    except Exception as e:
        print(f"[printer] Utskrift misslyckades: {e}")
        return False


def _detect_method(system: str) -> str:
    """Välj bästa utskriftsmetod för aktuellt OS."""
    if system == "Darwin" or system == "Linux":
        # Mac och Linux: lp finns alltid
        return "lp"
    elif system == "Windows":
        # Windows: SumatraPDF om installerat, annars os.startfile
        if shutil.which("SumatraPDF") or shutil.which("SumatraPDF.exe"):
            return "sumatrapdf"
        return "osprint"
    return "lp"


def _print_lp(pdf_path: str, printer_name: str) -> bool:
    """Skriv ut via lp (Mac/Linux)."""
    cmd = ["lp"]
    if printer_name and printer_name != "default":
        cmd.extend(["-d", printer_name])
    cmd.append(pdf_path)

    print(f"[printer] Kör: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"[printer] Utskrift skickad: {pdf_path}")
        return True
    else:
        print(f"[printer] lp misslyckades: {result.stderr}")
        return False


def _print_sumatrapdf(pdf_path: str, printer_name: str) -> bool:
    """Skriv ut via SumatraPDF (Windows)."""
    exe = shutil.which("SumatraPDF") or shutil.which("SumatraPDF.exe") or "SumatraPDF"

    if printer_name and printer_name != "default":
        cmd = [exe, "-print-to", printer_name, pdf_path]
    else:
        cmd = [exe, "-print-to-default", pdf_path]

    print(f"[printer] Kör: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"[printer] Utskrift skickad: {pdf_path}")
        return True
    else:
        print(f"[printer] SumatraPDF misslyckades: {result.stderr}")
        return False


def _print_os(pdf_path: str) -> bool:
    """Skriv ut via OS-inbyggd funktion (Windows os.startfile)."""
    if platform.system() != "Windows":
        print("[printer] os.startfile finns bara på Windows")
        return False

    print(f"[printer] Skriver ut via Windows shell: {pdf_path}")
    os.startfile(pdf_path, "print")
    return True


# ---------------------------------------------------------------------------
#  CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Användning: python printer.py <fil.pdf> [skrivarnamn]")
        sys.exit(1)

    pdf = sys.argv[1]
    name = sys.argv[2] if len(sys.argv) >= 3 else "default"

    ok = print_pdf(pdf, printer_name=name)
    sys.exit(0 if ok else 1)
