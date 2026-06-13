"""Render TCSE_v2.19.docx to PDF via LibreOffice headless and report the page
count plus how full the last page is. Fill % = (bottom of lowest text on the
last page - top margin) / (page height - top margin - bottom margin). Read-only:
does not modify the docx. Usage: _measure_fill.py"""
import subprocess
import sys
from pathlib import Path

import fitz

sys.stdout.reconfigure(encoding="utf-8")
SRC = Path("paper/TCSE_v2.19.docx").resolve()
SOFFICE = r"C:\Program Files\LibreOffice\program\soffice.exe"
OUT = Path("paper/_render").resolve()


def render_pdf(out_dir):
    subprocess.run(
        [SOFFICE, "--headless", "--convert-to", "pdf", "--outdir", out_dir, str(SRC)],
        check=True, capture_output=True,
    )
    return Path(out_dir) / (SRC.stem + ".pdf")


def main():
    OUT.mkdir(exist_ok=True)
    pdf = render_pdf(str(OUT))
    doc = fitz.open(pdf)
    n = doc.page_count
    last = doc[n - 1]
    H = last.rect.height
    # Detect actual top/bottom margins from page-1 text extent (full page).
    p1 = doc[0]
    b1 = [b for b in p1.get_text("blocks") if b[4].strip()]
    margin = min(b[1] for b in b1)  # top text start on a full page ~ top margin
    blocks = [b for b in last.get_text("blocks") if b[4].strip()]
    if not blocks:
        print(f"pages={n} last page EMPTY")
        doc.close()
        return
    top = min(b[1] for b in blocks)
    bottom = max(b[3] for b in blocks)
    usable = H - 2 * margin
    fill = (bottom - margin) / usable * 100
    print(f"pages={n}")
    print(f"detected top-margin={margin:.1f}pt")
    print(f"last-page height={H:.1f}pt  top-text={top:.1f}  bottom-text={bottom:.1f}")
    print(f"fill%={fill:.1f}  (usable {usable:.0f}pt, bottom gap {H - margin - bottom:.1f}pt)")
    lines = last.get_text().strip().splitlines()
    print("--- last 3 lines on last page ---")
    for ln in lines[-3:]:
        print("  ", ln[:80])
    doc.close()


if __name__ == "__main__":
    main()
