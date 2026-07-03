import sys
from pathlib import Path
from docx import Document
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

sys.stdout.reconfigure(encoding="utf-8")
src = Path(sys.argv[1])
doc = Document(src)
body = doc.element.body
tidx = 0
for child in body.iterchildren():
    if child.tag == qn("w:tbl"):
        tbl = Table(child, doc)
        tidx += 1
        print(f"\n===== TABLE {tidx}  ({len(tbl.rows)}x{len(tbl.columns)}) =====")
        for r in tbl.rows:
            cells = [c.text.strip().replace("\n"," / ") for c in r.cells]
            print(" | ".join(cells))
