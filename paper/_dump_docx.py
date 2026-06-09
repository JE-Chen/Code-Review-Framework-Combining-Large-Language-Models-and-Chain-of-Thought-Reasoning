"""Dump a .docx to a readable text outline (paragraph index, style, image/table
markers, text) so the rewrite can see exact anchors. One-off helper, mirrors the
underscore-prefixed paper/ scripts. Usage: python _dump_docx.py <file.docx>"""
import sys
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

sys.stdout.reconfigure(encoding="utf-8")
src = Path(sys.argv[1])
doc = Document(src)


def has_img(p):
    return bool(p._p.findall(".//" + qn("w:drawing")))


body = doc.element.body
lines = []
pi = 0
for child in body.iterchildren():
    if child.tag == qn("w:p"):
        p = Paragraph(child, doc)
        txt = p.text.strip()
        img = " [IMG]" if has_img(p) else ""
        style = p.style.name if p.style else "?"
        sz = None
        for r in p.runs:
            if r.text.strip() and r.font.size:
                sz = r.font.size.pt
                break
        sztag = f" {sz}pt" if sz else ""
        if txt or img:
            lines.append(f"[{pi:04d}] <{style}{sztag}>{img} {txt[:300]}")
        pi += 1
    elif child.tag == qn("w:tbl"):
        tbl = Table(child, doc)
        nrows, ncols = len(tbl.rows), len(tbl.columns)
        first = " | ".join(c.text.strip()[:20] for c in tbl.rows[0].cells[:ncols])
        lines.append(f"[TABLE {nrows}x{ncols}] hdr: {first}")

out = src.with_name(f"_dump_{src.stem}.txt")
out.write_text("\n".join(lines), encoding="utf-8")
print(f"wrote {out} ({len(lines)} blocks)")
