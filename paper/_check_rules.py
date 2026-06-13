"""Check a paper .docx against the paper-author hard rules (REWRITE_BRIEF §1):
half-width punctuation, full-width semicolons (子句以「，」連接、避免「；」),
first-occurrence-only glosses, 標楷體/Times New Roman fonts, Chinese-numeral
figure/table numbering, citation range, and AI-tool-name leakage. One-off
helper, mirrors the underscore-prefixed paper/ scripts.
Usage: python _check_rules.py <file.docx>"""
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

sys.stdout.reconfigure(encoding="utf-8")
src = Path(sys.argv[1])
doc = Document(src)

CJK = r"一-鿿"


def iter_blocks():
    """Yield (index, kind, text) for body paragraphs and table cells."""
    body = doc.element.body
    pi = 0
    for child in body.iterchildren():
        if child.tag == qn("w:p"):
            yield pi, "p", Paragraph(child, doc).text
            pi += 1
        elif child.tag == qn("w:tbl"):
            tbl = Table(child, doc)
            for r in tbl.rows:
                for c in r.cells:
                    yield pi, "tbl", c.text
            pi += 1


def show(idx, kind, text, m):
    lo, hi = max(0, m.start() - 18), min(len(text), m.end() + 18)
    print(f"  [{idx:04d}/{kind}] …{text[lo:hi]}…")


print(f"==== {src.name} ====")

print("\n-- 規則1：中文行文之半形標點（命中需人工確認是否屬例外） --")
pat1 = re.compile(
    rf"[{CJK}][,;:?!()]|[,;:?!(][{CJK}]|[{CJK}]\.(?![a-zA-Z0-9])"
    rf"|[{CJK}] [(]|[)] [{CJK}]"
)
n1 = 0
for idx, kind, text in iter_blocks():
    for m in pat1.finditer(text):
        show(idx, kind, text, m)
        n1 += 1
print(f"  共 {n1} 處")

print("\n-- 規則1b：全形分號「；」（規則為子句以「，」連接、避免「；」） --")
n1b = 0
for idx, kind, text in iter_blocks():
    for m in re.finditer("；", text):
        show(idx, kind, text, m)
        n1b += 1
print(f"  共 {n1b} 處（應為 0）")

print("\n-- 規則2：中英 gloss 出現位置（同一英文名 >1 次即疑似重複解釋） --")
pat2 = re.compile(r"（([A-Za-z][A-Za-z0-9\- ]{2,})[,，）]")
seen: dict = {}
for idx, kind, text in iter_blocks():
    for m in pat2.finditer(text):
        seen.setdefault(m.group(1).strip().lower(), []).append(idx)
for name, idxs in sorted(seen.items()):
    flag = "  <== 重複" if len(idxs) > 1 else ""
    print(f"  {name}: 段 {idxs}{flag}")

print("\n-- 規則3：字型（run 層 rFonts 統計，document.xml） --")
with zipfile.ZipFile(src) as z:
    xml = z.read("word/document.xml").decode("utf-8")
    styles = z.read("word/styles.xml").decode("utf-8")
runs = re.findall(r"<w:r\b[^>]*>.*?</w:r>", xml, re.S)
font_counter: Counter = Counter()
no_rfonts = 0
for r in runs:
    if "<w:t" not in r:
        continue
    mf = re.search(r"<w:rFonts ([^/>]*)/?>", r)
    if not mf:
        no_rfonts += 1
        continue
    attrs = dict(re.findall(r'w:(\w+)="([^"]*)"', mf.group(1)))
    key = (attrs.get("ascii"), attrs.get("eastAsia"),
           attrs.get("hAnsi"), attrs.get("cs"))
    font_counter[key] += 1
print(f"  有文字之 run 無 rFonts（靠樣式繼承）：{no_rfonts}")
for key, n in font_counter.most_common():
    print(f"  ascii={key[0]} eastAsia={key[1]} hAnsi={key[2]} cs={key[3]}: {n}")
md = re.search(r"<w:docDefaults>.*?</w:docDefaults>", styles, re.S)
if md:
    mf = re.search(r"<w:rFonts ([^/>]*)/?>", md.group(0))
    print(f"  docDefaults rFonts: {mf.group(1) if mf else '(無)'}")
# 真正會出問題的兩種：含中文卻非標楷體；含英文字母卻設成標楷體（審稿意見5）。
cjk_re = re.compile(rf"[{CJK}]")
latin_re = re.compile(r"[A-Za-z]")
bad_cjk = bad_latin = 0
for r in doc.element.body.findall(".//" + qn("w:r")):
    txt = "".join(t.text or "" for t in r.findall(qn("w:t")))
    rpr = r.find(qn("w:rPr"))
    rf = rpr.find(qn("w:rFonts")) if rpr is not None else None
    ea = rf.get(qn("w:eastAsia")) if rf is not None else None
    asc = rf.get(qn("w:ascii")) if rf is not None else None
    if cjk_re.search(txt) and ea != "標楷體":
        bad_cjk += 1
    if latin_re.search(txt) and asc == "標楷體":
        bad_latin += 1
print(f"  含中文卻非標楷體之 run：{bad_cjk}（應為 0）")
print(f"  含英文卻設標楷體之 run：{bad_latin}（應為 0，對應審稿意見5）")

print("\n-- 規則4：中文段落內之阿拉伯數字圖表編號 --")
# 只認「圖1」「圖 1」「表 2」這類緊鄰之阿拉伯編號；不認 Tab 分隔（那是
# 目錄裡「…系統架構圖<Tab>24」的頁碼，屬誤報）。
pat4 = re.compile(r"[圖表][ 　]?[0-9][0-9-]*")
n4 = 0
for idx, kind, text in iter_blocks():
    if not re.search(rf"[{CJK}]", text):
        continue
    for m in pat4.finditer(text):
        show(idx, kind, text, m)
        n4 += 1
print(f"  共 {n4} 處")

print("\n-- 規則5：引用編號範圍與表圖數據引用 --")
cites = Counter()
for idx, kind, text in iter_blocks():
    for m in re.finditer(r"\[(\d{1,3})\]", text):
        cites[int(m.group(1))] += 1
if cites:
    print(f"  使用之引用編號：{sorted(cites)}（最大 {max(cites)}）")
    bad = [n for n in cites if n > 22]
    print(f"  超出 [22]：{bad if bad else '無'}")
else:
    print("  無 [N] 引用")
nums = re.compile(r"0\.\d{2}|\+\s?3?4 分|\+\s?2 分|44 筆")
print("  含關鍵數據卻未提及表/圖之段落：")
n5 = 0
for idx, kind, text in iter_blocks():
    if kind != "p" or not nums.search(text):
        continue
    if not re.search(r"[表圖]", text):
        print(f"  [{idx:04d}] {text[:120]}")
        n5 += 1
print(f"  共 {n5} 段（需人工確認）")

print("\n-- 規則6：AI 工具掛名洩漏（署名語永遠禁止；被評比模型名屬實驗事實，允許） --")
# 這些片語暗示「以 AI 工具撰寫本文」，永遠禁止。
forbidden = re.compile(
    r"AI-generated|Co-Authored-By|Claude Code|由\s*Claude\s*(?:撰寫|生成|產生|協助)"
    r"|本文.*(?:由|使用).*(?:Claude|GPT|Copilot).*(?:撰寫|生成)",
    re.I)
nf6 = 0
for idx, kind, text in iter_blocks():
    for m in forbidden.finditer(text):
        show(idx, kind, text, m)
        nf6 += 1
print(f"  署名語違規：{nf6} 處（應為 0）")
# 模型名提及——逐處確認屬「被評比/被使用之模型」而非掛名（允許，僅列出供人工複核）。
model_re = re.compile(r"GPT-5|Gemini-3|Claude|Copilot|Anthropic|OpenAI")
hits = Counter()
for idx, kind, text in iter_blocks():
    for m in model_re.finditer(text):
        hits[m.group(0)] += 1
print(f"  被評比/被使用之模型名提及（允許，供複核）：{dict(hits)}")
