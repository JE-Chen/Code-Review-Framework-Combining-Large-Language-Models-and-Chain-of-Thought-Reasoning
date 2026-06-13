"""Enforce paper-author rule 3 on a .docx without touching anything else:
every content run (CJK / Latin / digit / full-width punctuation) gets an
explicit four-slot <w:rFonts> — ascii/hAnsi/cs = Times New Roman, eastAsia =
標楷體 — so no run falls back to docDefaults (which here resolves CJK to
新細明體, a violation). Math runs (Cambria Math) and emoji/symbol-only runs
are left untouched so equations and 👎 reactions keep their fonts.
One-off helper, mirrors the underscore-prefixed paper/ scripts.
Usage: .venv/Scripts/python.exe paper/_fix_fonts.py <in.docx> <out.docx>"""
import re
import sys

from docx import Document
from docx.oxml.ns import qn

sys.stdout.reconfigure(encoding="utf-8")
src, dst = sys.argv[1], sys.argv[2]
doc = Document(src)
body = doc.element.body
W_T, W_R, W_RPR, W_RFONTS = qn("w:t"), qn("w:r"), qn("w:rPr"), qn("w:rFonts")

# CJK ideographs, CJK punctuation, full-width forms, and ASCII letters/digits.
HAS_CONTENT = re.compile(r"[A-Za-z0-9一-鿿　-〿＀-￯]")
EAST_ASIA = "標楷體"
LATIN = "Times New Roman"

fixed = skipped_math = skipped_symbol = 0
for r in body.findall(".//" + W_R):
    text = "".join(t.text or "" for t in r.findall(W_T))
    if not text or not HAS_CONTENT.search(text):
        skipped_symbol += 1
        continue
    rpr = r.find(W_RPR)
    rfonts = rpr.find(W_RFONTS) if rpr is not None else None
    # Preserve math runs — forcing Times New Roman would kill equation italics.
    if rfonts is not None and rfonts.get(qn("w:ascii")) == "Cambria Math":
        skipped_math += 1
        continue
    if rpr is None:
        rpr = r.makeelement(W_RPR, {})
        r.insert(0, rpr)
    if rfonts is None:
        rfonts = rpr.makeelement(W_RFONTS, {})
        rpr.insert(0, rfonts)
    for slot in ("w:ascii", "w:hAnsi", "w:cs"):
        rfonts.set(qn(slot), LATIN)
    rfonts.set(qn("w:eastAsia"), EAST_ASIA)
    fixed += 1

doc.save(dst)
print(f"{src} -> {dst}")
print(f"  改字型 {fixed} 個 run；保留數學 {skipped_math}；略過符號/空白 {skipped_symbol}")
