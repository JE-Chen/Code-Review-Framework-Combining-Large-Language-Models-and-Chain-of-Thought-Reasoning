"""Produce TCSE_v2.13.docx from TCSE_v2.12.docx (original untouched): mirror the
single-judge (Claude) CRSCORE++ narrative chosen for the thesis. 表一's Ours
column becomes gemma-4-31B-it's Claude scores (1.00/0.79/0.86); a short caption
note carries the equal same-judge previous-model score (1.00/0.78/0.86) and the
judge disclosures; the abstract, §5.2 and §6.1 drop the 0.86 GPT-5 headline for
the same-judge framing. Numbers come from the committed score files; prose names
the previous model only through the table/caption. Kept concise for the 6-page
limit. One-off helper, mirrors the underscore-prefixed paper/ scripts.
Usage: .venv/Scripts/python.exe paper/_rewrite_tcse_v213.py"""
import copy
import re
import sys

from docx import Document
from docx.oxml.ns import qn

sys.stdout.reconfigure(encoding="utf-8")
SRC, DST = "paper/TCSE_v2.12.docx", "paper/TCSE_v2.13.docx"
doc = Document(SRC)
body = doc.element.body
W_T, W_P, W_R, W_RPR = qn("w:t"), qn("w:p"), qn("w:r"), qn("w:rPr")


def paras():
    return body.findall(".//" + W_P)


def para_text(p):
    return "".join(t.text or "" for t in p.findall(".//" + W_T))


def set_text(t, s):
    t.text = s
    if s != s.strip():
        t.set(qn("xml:space"), "preserve")


def _rewrite_spans(spans, idx, end, new):
    first = True
    for a, b, t in spans:
        if b <= idx or a >= end:
            continue
        seg = t.text or ""
        lo, hi = max(idx - a, 0), min(end - a, len(seg))
        set_text(t, seg[:lo] + (new if first else "") + seg[hi:])
        first = False


def replace_once(old, new):
    for p in paras():
        ts = p.findall(".//" + W_T)
        joined, spans = "", []
        for t in ts:
            s = t.text or ""
            spans.append((len(joined), len(joined) + len(s), t))
            joined += s
        idx = joined.find(old)
        if idx != -1:
            _rewrite_spans(spans, idx, idx + len(old), new)
            return True
    raise SystemExit(f"定點改寫未命中：{old[:40]}…")


def set_cell(cell, value):
    ts = cell._tc.findall(".//" + W_T)
    if ts:
        set_text(ts[0], value)
        for t in ts[1:]:
            set_text(t, "")
    else:
        p = cell._tc.find(".//" + W_P)
        r = p.makeelement(W_R, {})
        t = r.makeelement(W_T, {})
        t.text = value
        r.append(t)
        p.append(r)


# ---------- 1. 表一：Ours 欄改 gemma 之 Claude 分數，其餘欄標 † ----------
tbl = next((t for t in doc.tables
            if any("CRSCORE" in c.text for c in t.rows[0].cells)
            and any("Qwen3-Coder" in c.text for c in t.rows[0].cells)), None)
if tbl is None:
    raise SystemExit("找不到表一（CRSCORE++ 整體評估）")
hdrs = [c.text.strip() for c in tbl.rows[0].cells]
i_ours = next(i for i, h in enumerate(hdrs) if "Qwen3-Coder" in h)
i_others = [i for i, h in enumerate(hdrs)
            if i not in (0, i_ours) and ("CRSCORE" in h or "7B" in h or "7b" in h)]
set_cell(tbl.rows[0].cells[i_ours], "Ours\n(gemma-4-31B-it)")
for r, val in zip((1, 2, 3), ("1.00", "0.79", "0.86")):  # comp / concise / relev
    set_cell(tbl.rows[r].cells[i_ours], val)
for i in i_others:
    set_cell(tbl.rows[0].cells[i], hdrs[i] + " †")
print("表一：Ours 欄改 gemma，其餘欄標 †")

# ---------- 2. 表一標題後補簡短 judge 揭露註 ----------
cap = next((p for p in paras() if para_text(p).strip().startswith("表一")
            and "整體評估" in para_text(p)), None)
if cap is None:
    raise SystemExit("找不到表一標題段")
note = copy.deepcopy(cap)
nts = note.findall(".//" + W_T)
set_text(
    nts[0],
    "註：Ours 欄為 gemma-4-31B-it（judge：Claude）；同一 judge 下前代學生模型為 "
    "1.00／0.78／0.86，二者相等；標 † 欄為不同 judge 之參考，該 judge 對完整性"
    "普遍給滿分。",
)
for t in nts[1:]:
    set_text(t, "")
cap.addnext(note)
print("表一：補入簡短 judge 揭露註")

# ---------- 3. 摘要、§5.2、§6.1 之同 judge 改寫（精簡） ----------
EDITS = [
    ("於 CRSCORE++ 指標上，本框架之 comprehensiveness、relevance 與 conciseness "
     "分別達 0.86、0.83 與 0.64（皆介於 0 至 1，越接近 1 越好），均優於基準。",
     "於 CRSCORE++ 指標上，以同一 judge 評分，本框架以 gemma-4-31B-it 與前代學生"
     "模型為基底之品質相當（1.00／0.79／0.86 對 1.00／0.78／0.86），且高於基準；"
     "完整性因該 judge 飽和而資訊量有限。"),
    ("所提出之整合框架相較 CRSCORE++，在 comprehensiveness（0.86 vs 0.67）、"
     "conciseness（0.64 vs 0.57）與 relevance（0.83 vs 0.63）三個面向皆明顯提升"
     "（表一，三項皆介於 0 至 1，越接近 1 越好），其中以完整性之增幅最為明顯："
     "0.86 對 0.67 代表更少漏看真正該提的問題，此即多階段拆解、RAG 規則注入與微調"
     "整合後的整體效果。",
     "以同一 judge（Claude）評分，本框架以 gemma-4-31B-it 與前代學生模型為基底之 "
     "CRSCORE++ 三維度幾乎相等（1.00／0.79／0.86 對 1.00／0.78／0.86，表一），顯示"
     "更換基座未損及審查品質；二者於簡潔性與相關性高於 CRSCORE++ 基準，惟基準為"
     "不同 judge、完整性因評審飽和而資訊量有限。"),
    ("所提框架於完整性、簡潔性與相關性面向均優於基準（表一：0.86 / 0.64 / 0.83 對 "
     "0.67 / 0.57 / 0.63），並由人工評分交叉驗證。",
     "於同一 judge 下，所提框架以 gemma-4-31B-it 與前代學生模型為基底之品質相當"
     "（表一：1.00 / 0.79 / 0.86 對 1.00 / 0.78 / 0.86），並由人工評分交叉驗證。"),
]
for old, new in EDITS:
    replace_once(old, new)
print(f"摘要／§5.2／§6.1 改寫 {len(EDITS)} 處")

# ---------- 全形標點正規化 ----------
PUNCT_MAP = {",": "，", ";": "，", ":": "：", "?": "？", "!": "！"}


def _cjkish(ch):
    return ("一" <= ch <= "鿿" or "　" <= ch <= "〿"
            or "＀" <= ch <= "￯" or ch in "—…•")


def _nearest_visible(seq):
    return next((c for c in seq if c != " "), "")


def _paren_is_cjk(text, j, i):
    seg_cjk = any(_cjkish(c) for c in text[j + 1:i])
    prev = _nearest_visible(reversed(text[:j]))
    nxt = _nearest_visible(text[i + 1:])
    return seg_cjk or (bool(prev) and _cjkish(prev)) or (bool(nxt) and _cjkish(nxt))


def _convert_parens(text, chars):
    stack = []
    for i, ch in enumerate(chars):
        if ch == "(":
            stack.append(i)
        elif ch == ")" and stack:
            j = stack.pop()
            if _paren_is_cjk(text, j, i):
                chars[j], chars[i] = "（", "）"


def _convert_marks(chars):
    for i, ch in enumerate(chars):
        if ch in PUNCT_MAP:
            prev = _nearest_visible(reversed(chars[:i]))
            nxt = _nearest_visible(chars[i + 1:])
            if _cjkish(prev) or _cjkish(nxt):
                chars[i] = PUNCT_MAP[ch]


def convert_punct(text):
    chars = list(text)
    _convert_parens(text, chars)
    _convert_marks(chars)
    return "".join(chars)


np = 0
for p in paras():
    ts = p.findall(".//" + W_T)
    joined = "".join(t.text or "" for t in ts)
    conv = convert_punct(joined)
    if conv != joined:
        pos = 0
        for t in ts:
            n = len(t.text or "")
            set_text(t, conv[pos:pos + n])
            pos += n
        np += 1
print(f"標點正規化：{np} 段")

# ---------- 字型 ----------
HAS_CONTENT = re.compile(r"[A-Za-z0-9一-鿿　-〿＀-￯]")
nf = 0
for r in body.findall(".//" + W_R):
    s = "".join(t.text or "" for t in r.findall(W_T))
    if not s or not HAS_CONTENT.search(s):
        continue
    rpr = r.find(W_RPR)
    if rpr is None:
        rpr = r.makeelement(W_RPR, {})
        r.insert(0, rpr)
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = rpr.makeelement(qn("w:rFonts"), {})
        rpr.insert(0, rf)
    for slot in ("w:ascii", "w:hAnsi", "w:cs"):
        rf.set(qn(slot), "Times New Roman")
    rf.set(qn("w:eastAsia"), "標楷體")
    nf += 1
print(f"字型設定：{nf} 個 run")

doc.save(DST)
print(f"已輸出 {DST}")
