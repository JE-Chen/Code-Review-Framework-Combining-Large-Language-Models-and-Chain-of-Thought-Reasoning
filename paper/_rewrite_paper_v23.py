"""Produce 論文_v2.3.docx from 論文_v2.2.docx (original untouched): a
ThesisAgents-handbook copy-edit pass. Fixes (all verified against the
v2.2 dump): move the gemma-4-31B-it provider gloss to its first chronological
use, drop the banned AI-tell 深入探討, correct Simplified-Chinese loan words
to Traditional-Chinese standard vocabulary (信號→訊號, 調用→呼叫, 顯存→
顯示記憶體, 設置→設定, 優化器→最佳化器, 數組→多組), and remove a
drafting-metadata leak (an internal .rst path). No empirical claim, number,
table, or model attribution is changed. One-off helper, mirrors the
underscore-prefixed paper/ scripts.
Usage: .venv/Scripts/python.exe paper/_rewrite_paper_v23.py"""
import re
import sys

from docx import Document
from docx.oxml.ns import qn

sys.stdout.reconfigure(encoding="utf-8")
SRC, DST = "paper/論文_v2.2.docx", "paper/論文_v2.3.docx"
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


def replace_everywhere(old, new, required=True):
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
    if required and n == 0:
        raise SystemExit(f"定點改寫未命中：{old[:40]}…")
    return n


# ---------- 1. 定點改寫（gloss 前移、AI 口頭禪、簡體用詞、元資訊洩漏） ----------
EDITS = [
    # 首次出現之 gemma-4-31B-it 補 provider gloss（手冊：模型名首次出現須附
    # 來源與角色），並把 bf16 dtype 由括號移至動詞前，避免與 gloss 並置
    ("線上推論以本機後端（LocalHF）載入現行基底 gemma-4-31B-it（bf16），"
     "掛載微調所得之 LoRA 適配器",
     "線上推論以本機後端（LocalHF）以 bf16 載入現行基底 gemma-4-31B-it"
     "（Google 釋出之開放權重大型語言模型），掛載微調所得之 LoRA 適配器"),
    # AI 口頭禪：深入探討 → 探討
    ("值得深入探討之方向", "值得探討之方向"),
    # 簡體常用語 → 繁體標準（語義不變）
    ("參數設置", "參數設定"),               # setting（名詞）→ 設定
    ("降低顯存佔用", "降低顯示記憶體佔用"),  # GPU memory
    ("掛載數組可選", "掛載多組可選"),        # 數組(array)誤用為「數組」→ 多組
    ("分頁優化器", "分頁最佳化器"),          # optimizer：學術以最佳化為佳
    # 草稿管理元資訊洩漏：移除指向寫作流程之內部 .rst 路徑
    ("（docs/en/concepts/research-extensions.rst）", ""),
]
for old, new in EDITS:
    print(f"改寫 {replace_everywhere(old, new)} 處：{(new or '〔刪除〕')[:24]}…")

# 全域簡體用詞（多處）：信號→訊號、調用→呼叫
print(f"信號→訊號 {replace_everywhere('信號', '訊號')} 處")
print(f"調用→呼叫 {replace_everywhere('調用', '呼叫')} 處")

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
