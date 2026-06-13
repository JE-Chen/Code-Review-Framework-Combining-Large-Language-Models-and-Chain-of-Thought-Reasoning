"""Replace every full-width semicolon 「；」 with 「，」 in a .docx, per
REWRITE_BRIEF §1.3 (子句以「，」連接，避免「；」堆疊). 「；」 is a single
character that never spans runs, so each <w:t> text node is edited in place —
fonts, runs, tables and images are untouched. English text and references use
the half-width ';', which is left alone. One-off helper, mirrors the
underscore-prefixed paper/ scripts.
Usage: .venv/Scripts/python.exe paper/_fix_semicolon.py <in.docx> <out.docx>"""
import sys

from docx import Document
from docx.oxml.ns import qn

sys.stdout.reconfigure(encoding="utf-8")
src, dst = sys.argv[1], sys.argv[2]
doc = Document(src)
W_T = qn("w:t")

n = 0
for t in doc.element.body.findall(".//" + W_T):
    if t.text and "；" in t.text:
        n += t.text.count("；")
        t.text = t.text.replace("；", "，")

doc.save(dst)
print(f"{src} -> {dst}：全形；改，共 {n} 處")
