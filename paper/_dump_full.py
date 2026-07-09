import sys
from pathlib import Path
from docx import Document
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph
sys.stdout.reconfigure(encoding="utf-8")
src = Path(sys.argv[1])
doc = Document(src)
body = doc.element.body
pi = 0
want = set(int(x) for x in sys.argv[2:])
for child in body.iterchildren():
    if child.tag == qn("w:p"):
        p = Paragraph(child, doc)
        txt = p.text.strip()
        if pi in want and txt:
            print(f"\n[{pi:04d}] {txt}")
        pi += 1
