"""Produce TCSE_v2.14.docx from TCSE_v2.13.docx (original untouched): trim ~200
characters so the paper returns to 6 pages. The CRSCORE++ numbers now live only
in 表一 and its caption note (single source); the repeated number-tuples are
removed from the abstract, §5.2 and §6.1 prose, which reference 表一 instead, and
the §6.2 / caption sentences are tightened. No claim or number is changed; only
redundant repetition is cut. One-off helper, mirrors the underscore-prefixed
paper/ scripts. Usage: .venv/Scripts/python.exe paper/_rewrite_tcse_v214.py"""
import re
import sys

from docx import Document
from docx.oxml.ns import qn

sys.stdout.reconfigure(encoding="utf-8")
SRC, DST = "paper/TCSE_v2.13.docx", "paper/TCSE_v2.14.docx"
doc = Document(SRC)
body = doc.element.body
W_T, W_P, W_R, W_RPR = qn("w:t"), qn("w:p"), qn("w:r"), qn("w:rPr")


def paras():
    return body.findall(".//" + W_P)


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


EDITS = [
    # 摘要：移除重複之數字組，改引表一
    ("於 CRSCORE++ 指標上，以同一 judge 評分，本框架以 gemma-4-31B-it 與前代學生"
     "模型為基底之品質相當（1.00／0.79／0.86 對 1.00／0.78／0.86），且高於基準；"
     "完整性因該 judge 飽和而資訊量有限。",
     "於 CRSCORE++ 指標上，同一 judge 下本框架以 gemma-4-31B-it 與前代學生模型為"
     "基底之品質相當（見表一），且高於基準；完整性因評審飽和而參考性有限。"),
    # §5.2：移除重複數字組
    ("以同一 judge（Claude）評分，本框架以 gemma-4-31B-it 與前代學生模型為基底之 "
     "CRSCORE++ 三維度幾乎相等（1.00／0.79／0.86 對 1.00／0.78／0.86，表一），顯示"
     "更換基座未損及審查品質；二者於簡潔性與相關性高於 CRSCORE++ 基準，惟基準為"
     "不同 judge、完整性因評審飽和而資訊量有限。",
     "以同一 judge（Claude）評分，本框架以 gemma-4-31B-it 與前代學生模型為基底之 "
     "CRSCORE++ 三維度幾乎相等（表一），顯示更換基座未損及審查品質；二者於簡潔性"
     "與相關性高於基準，惟基準為不同 judge、完整性因飽和而參考性有限。"),
    # §6.1：移除重複數字組
    ("於同一 judge 下，所提框架以 gemma-4-31B-it 與前代學生模型為基底之品質相當"
     "（表一：1.00 / 0.79 / 0.86 對 1.00 / 0.78 / 0.86），並由人工評分交叉驗證。",
     "於同一 judge 下，所提框架以 gemma-4-31B-it 與前代學生模型為基底之品質相當"
     "（表一），並由人工評分交叉驗證。"),
    # §6.2：精簡
    ("另，框架基底已更換為 gemma-4-31B-it 並於同一基準與管線完成重放，以同一 judge "
     "重評之 CRSCORE++ 顯示其與前代學生模型幾乎相等，餘屬未來工作。",
     "另，框架基底已更換為 gemma-4-31B-it 並完成同基準重放，同 judge 重評顯示與前代"
     "相當，餘屬未來工作。"),
    # 表一註：精簡（完整性飽和已於摘要說明）
    ("註：Ours 欄為 gemma-4-31B-it（judge：Claude）；同一 judge 下前代學生模型為 "
     "1.00／0.78／0.86，二者相等；標 † 欄為不同 judge 之參考，該 judge 對完整性"
     "普遍給滿分。",
     "註：Ours 欄為 gemma-4-31B-it（Claude 評）；同 judge 下前代基底為 "
     "1.00／0.78／0.86，二者相等；† 欄為不同 judge 之參考。"),
]
for old, new in EDITS:
    replace_once(old, new)
print(f"精簡改寫 {len(EDITS)} 處")

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
