"""Produce TCSE_v2.12.docx from TCSE_v2.11.docx (original untouched): shorten the
§6.2 cross-model sentence to a single conclusion clause to bring the paper back
under the 6-page limit. No number, table, or other content is changed.
One-off helper, mirrors the underscore-prefixed paper/ scripts.
Usage: .venv/Scripts/python.exe paper/_rewrite_tcse_v212.py"""
import re
import sys

from docx import Document
from docx.oxml.ns import qn

sys.stdout.reconfigure(encoding="utf-8")
SRC, DST = "paper/TCSE_v2.11.docx", "paper/TCSE_v2.12.docx"
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


OLD = (
    "另，跨模型重放已完成——框架基底現已更換為 gemma-4-31B-it 並加掛專屬 LoRA "
    "轉接器，於同一 44 筆基準資料與同一管線端到端重放；以同一 judge（Claude）重評 "
    "gemma 與前代學生模型之 CRSCORE++，二者三維幾乎相等（1.00／0.79／0.86 對 "
    "1.00／0.78／0.86），先前以不同 judge 觀察到之差異主要反映評審寬鬆度而非模型"
    "能力。本文表一至表三之數字仍保留前代學生模型配置（如表一欄名所列）之原始評分"
    "未動，其餘維度與成本延遲之比較仍屬未來工作。"
)
NEW = (
    "另，框架基底已更換為 gemma-4-31B-it 並於同一基準與管線完成重放，以同一 judge "
    "重評之 CRSCORE++ 顯示其與前代學生模型幾乎相等，餘屬未來工作。"
)
replace_once(OLD, NEW)
print("§6.2 縮短為單句結論")

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
