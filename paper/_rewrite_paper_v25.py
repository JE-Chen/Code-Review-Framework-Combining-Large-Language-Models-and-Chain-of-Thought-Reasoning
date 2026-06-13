"""Produce 論文_v2.5.docx from 論文_v2.4.docx (original untouched): update the
§6.4.1 cross-model replay paragraph now that the CRSCORE++ comparison has been
run with a single judge (Claude) for both gemma-4-31B-it and Qwen3-Coder-30B.
The cited numbers come from the committed score files
(datas/Results/.../score.md and score_claude.md): gemma 1.00/0.79/0.86,
qwen 1.00/0.78/0.86 — statistically equivalent under one judge, with the
comprehensiveness saturation caveat stated honestly. Tables 6-13 keep their
original GPT-5/Gemini-3 scores. No table number is changed. One-off helper,
mirrors the underscore-prefixed paper/ scripts.
Usage: .venv/Scripts/python.exe paper/_rewrite_paper_v25.py"""
import re
import sys

from docx import Document
from docx.oxml.ns import qn

sys.stdout.reconfigure(encoding="utf-8")
SRC, DST = "paper/論文_v2.4.docx", "paper/論文_v2.5.docx"
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


OLD = (
    "惟其 CRSCORE++ 與 LLM-as-a-Judge-Our 之評審評分尚未執行，本論文不引用任何 "
    "gemma 系列之分數，表六至表十三之數字均屬表二所列前代學生模型配置之結果；"
    "跨模型之量化比較（含上述品質、成本與延遲之偏序對照）仍屬未來工作。"
)
NEW = (
    "其 CRSCORE++ 評審已以同一 judge（Claude）重評 gemma-4-31B-it 與表二／表六"
    "所列之前代學生模型兩者之 44 案，以消除跨 judge 寬鬆度之混淆：兩者於完整性、"
    "簡潔性、相關性三維分別為 1.00／0.79／0.86 與 1.00／0.78／0.86，差距甚微而可"
    "視為相等。惟須註明，該 judge 於全部 88 案皆將完整性評為滿分，此維度於本比較"
    "下資訊量有限；於簡潔性與相關性兩維亦呈相等。先前以不同 judge 觀察到之差異"
    "（表六 Ours-30B 欄為 GPT-5 評分、gemma 為 Claude 評分）主要反映評審寬鬆度，"
    "而非模型能力差距。表六至表十三之數字仍保留表二所列前代學生模型配置之原始"
    "評分未動；LLM-as-a-Judge-Our 五維之同 judge 重評，以及成本與延遲之偏序對照，"
    "仍屬未來工作。"
)
replace_once(OLD, NEW)
print("§6.4.1 更新為同 judge 跨模型比較結果")

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
