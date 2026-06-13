"""Produce TCSE_v2.9.docx from TCSE_v2.8.docx (original untouched): a
ThesisAgents-handbook copy-edit pass. The only change is moving the
gemma-4-31B-it provider gloss to its first chronological use (§1.2) and
dropping the now-duplicate gloss at §3.2, per the handbook's first-use
gloss rule. TCSE was already clean on AI-tell, filler, and Simplified-Chinese
vocabulary scans (it carries no §3.8 mechanism section), so no other edits.
No empirical claim, number, table, or model attribution is changed.
One-off helper, mirrors the underscore-prefixed paper/ scripts.
Usage: .venv/Scripts/python.exe paper/_rewrite_tcse_v29.py"""
import re
import sys

from docx import Document
from docx.oxml.ns import qn

sys.stdout.reconfigure(encoding="utf-8")
SRC, DST = "paper/TCSE_v2.8.docx", "paper/TCSE_v2.9.docx"
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
    """Blank out [idx, end) across the runs, writing new into the first hit."""
    first = True
    for a, b, t in spans:
        if b <= idx or a >= end:
            continue
        seg = t.text or ""
        lo, hi = max(idx - a, 0), min(end - a, len(seg))
        set_text(t, seg[:lo] + (new if first else "") + seg[hi:])
        first = False


def replace_once_in_para(p, old, new):
    ts = p.findall(".//" + W_T)
    joined, spans = "", []
    for t in ts:
        s = t.text or ""
        spans.append((len(joined), len(joined) + len(s), t))
        joined += s
    idx = joined.find(old)
    if idx == -1:
        return False
    _rewrite_spans(spans, idx, idx + len(old), new)
    return True


def replace_everywhere(old, new):
    if new and old in new:
        raise SystemExit(f"old 為 new 之子字串，會無窮替換：{old[:40]}…")
    n = 0
    for p in paras():
        while old in para_text(p):
            before = para_text(p)
            replace_once_in_para(p, old, new)
            if para_text(p) == before:
                raise SystemExit(f"替換無進展：{old[:40]}…")
            n += 1
    if n == 0:
        raise SystemExit(f"定點改寫未命中：{old[:40]}…")
    return n


# ---------- 1. 首次出現 gloss 前移（§1.2 補、§3.2 去重） ----------
EDITS = [
    # §1.2 構想：gemma 之首次出現，補 provider gloss
    ("輕量化學生模型（現行基底為 gemma-4-31B-it）",
     "輕量化學生模型（現行基底為 gemma-4-31B-it，Google 釋出之開放權重大型語言模型）"),
    # §3.2 輸入層：首次出現已於 §1.2 解釋，此處去重為裸名（不重複內容規則）
    ("啟動時載入審查模型 gemma-4-31B-it（Google 釋出之開放權重模型）與訓練完成之 LoRA 權重",
     "啟動時載入審查模型 gemma-4-31B-it 與訓練完成之 LoRA 權重"),
]
for old, new in EDITS:
    print(f"改寫 {replace_everywhere(old, new)} 處：{new[:24]}…")

# ---------- 2. 全形標點正規化（1:1 字元映射，按原 run 長度回填） ----------
PUNCT_MAP = {",": "，", ";": "，", ":": "：", "?": "？", "!": "！"}


def _cjkish(ch):
    return ("一" <= ch <= "鿿" or "　" <= ch <= "〿"
            or "＀" <= ch <= "￯" or ch in "—…•")


def _nearest_visible(seq):
    """First non-space char in seq, or '' when none."""
    return next((c for c in seq if c != " "), "")


def _paren_is_cjk(text, j, i):
    """True when the (j, i) paren pair sits in CJK context."""
    seg_cjk = any(_cjkish(c) for c in text[j + 1:i])
    prev = _nearest_visible(reversed(text[:j]))
    nxt = _nearest_visible(text[i + 1:])
    prev_cjk = bool(prev) and _cjkish(prev)
    nxt_cjk = bool(nxt) and _cjkish(nxt)
    return seg_cjk or prev_cjk or nxt_cjk


def _convert_parens(text, chars):
    """Full-width-ify balanced ASCII parens that sit in CJK context."""
    stack = []
    for i, ch in enumerate(chars):
        if ch == "(":
            stack.append(i)
        elif ch == ")" and stack:
            j = stack.pop()
            if _paren_is_cjk(text, j, i):
                chars[j], chars[i] = "（", "）"


def _convert_marks(chars):
    """Full-width-ify mapped punctuation adjacent to CJK text."""
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

# ---------- 3. 字型：每個含文字之 run 顯式四 slot ----------
# 中英文與全形標點 run 一律顯式設字型；純符號 run（✓/emoji/數學）保留原字型
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
