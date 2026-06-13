"""Produce TCSE_v2.7.docx from TCSE_v2.6.docx (original untouched), applying
the five paper-author hard rules: Chinese-numeral figure/table numbering
(圖 1 → 圖一 etc.), full-width punctuation in Chinese captions, explicit
標楷體/Times New Roman run fonts, and table citations for result claims.
One-off helper, mirrors the underscore-prefixed paper/ scripts.
Usage: .venv/Scripts/python.exe paper/_rewrite_tcse_v27.py"""
import copy
import re
import sys

from docx import Document
from docx.oxml.ns import qn

sys.stdout.reconfigure(encoding="utf-8")
SRC, DST = "paper/TCSE_v2.6.docx", "paper/TCSE_v2.7.docx"
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
    if old in new:
        raise SystemExit(f"old 為 new 之子字串，會無窮替換：{old[:40]}…")
    n = 0
    for p in paras():
        while old in para_text(p):
            before = para_text(p)
            replace_once_in_para(p, old, new)
            if para_text(p) == before:
                raise SystemExit(f"替換無進展（疑似跨結構 run）：{old[:40]}…")
            n += 1
    if required and n == 0:
        raise SystemExit(f"未命中：{old[:40]}…")
    return n


# ---------- 1. 題注格式統一（圖一、…／表一、…），再處理內文引用 ----------
EDITS = [
    ("圖1 系統架構圖", "圖一、系統架構圖"),
    ("圖2 訓練流程", "圖二、訓練流程"),
    ("圖3 LLM-as-a-Judge流程", "圖三、LLM-as-a-Judge 流程"),
    ("表1  CRSCORE++ 整體評估", "表一、CRSCORE++ 整體評估"),
    ("表2 提示詞設計比較 (LLM 評分)", "表二、提示詞設計比較（LLM 評分）"),
    ("表3 提示詞設計比較 (人工評分)", "表三、提示詞設計比較（人工評分）"),
]
for old, new in EDITS:
    print(f"題注 {replace_everywhere(old, new)} 處：{old} → {new}")

GENERIC = [("圖 1", "圖一"), ("圖 2", "圖二"), ("圖 3", "圖三"),
           ("表 1", "表一"), ("表 2", "表二"), ("表 3", "表三")]
for old, new in GENERIC:
    n = replace_everywhere(old, new, required=False)
    if n:
        print(f"內文引用 {n} 處：{old} → {new}")

# ---------- 2. 結果句補表格引用（數據出自表者必引其表） ----------
CITES = [
    ("三個面向皆顯著提升（三項皆介於 0 至 1，越接近 1 越好）",
     "三個面向皆顯著提升（表一，三項皆介於 0 至 1，越接近 1 越好）"),
    ("僅 conciseness 略遜，顯示即使未經微調",
     "僅 conciseness 略遜（表一），顯示即使未經微調"),
    ("均優於基準（0.86 / 0.64 / 0.83 對 0.67 / 0.57 / 0.63）",
     "均優於基準（表一：0.86 / 0.64 / 0.83 對 0.67 / 0.57 / 0.63）"),
]
for old, new in CITES:
    print(f"補引用 {replace_everywhere(old, new)} 處：…{new[-32:]}")

# ---------- 2b. 替換殘留空格（原「表 2 之」→「表二 之」之類） ----------
SPACE_FIX = [
    ("如圖一 所示", "如圖一所示"), ("如圖二 所示", "如圖二所示"), ("如圖三 所示", "如圖三所示"),
    ("表一 以", "表一以"), ("表二 拆解", "表二拆解"), ("表三 則為", "表三則為"),
    ("由表二 之", "由表二之"), ("表三 之人工評分結果與表二 之", "表三之人工評分結果與表二之"),
]
for old, new in SPACE_FIX:
    replace_everywhere(old, new)
print("空格清理完成")

# ---------- 2c. QLoRA 首次出現補英文原名（摘要與正文各一次）、CoT 黏字 ----------
GLOSS = [
    ("結合量化低秩適應（QLoRA）把教師模型",
     "結合量化低秩適應（Quantized Low-Rank Adaptation, QLoRA）把教師模型"),
    ("模型面採知識蒸餾結合 QLoRA，將教師模型",
     "模型面採知識蒸餾結合量化低秩適應（Quantized Low-Rank Adaptation, QLoRA），將教師模型"),
    ("思維鏈 CoT係一種", "思維鏈 CoT 係一種"),
]
for old, new in GLOSS:
    print(f"gloss/校稿 {replace_everywhere(old, new)} 處：{new[:36]}…")

# ---------- 2d. §5 改為 RQ1–RQ4 獨立子章節（審稿意見：逐一回答各 RQ） ----------
heading_53 = next((p for p in paras() if "5.3 人工評分交叉驗證" in para_text(p)), None)
if heading_53 is None:
    raise SystemExit("找不到 5.3 標題段")
for anchor, num, title in (
    ("RQ2：於相同參數量", "5.3 ", "RQ2：多階段提示詞之單獨效益"),
    ("RQ3：由表二之消融結果", "5.4 ", "RQ3：提示詞與微調之邊際貢獻"),
):
    target = next((p for p in paras() if anchor in para_text(p)), None)
    if target is None:
        raise SystemExit(f"找不到 RQ 段：{anchor}")
    clone = copy.deepcopy(heading_53)
    cts = clone.findall(".//" + W_T)
    set_text(cts[0], num)
    set_text(cts[1], title)
    for t in cts[2:]:
        set_text(t, "")
    target.addprevious(clone)
    print(f"插入子章節：{num}{title}")
RQ_EDITS = [
    ("5.2 自動化評估結果", "5.2 RQ1：整體品質與既有基準之比較"),
    ("5.3 人工評分交叉驗證", "5.5 RQ4：人工評分交叉驗證"),
    ("RQ1：所提出之整合框架", "所提出之整合框架"),
    ("RQ2：於相同參數量", "於相同參數量"),
    ("RQ3：由表二之消融結果", "由表二之消融結果"),
    ("RQ4：表三之人工評分結果", "表三之人工評分結果"),
]
for old, new in RQ_EDITS:
    print(f"RQ 結構 {replace_everywhere(old, new)} 處：{new[:30]}…")

# ---------- 2e. 審稿意見：無統計檢定不稱「顯著」；限制節補統計檢定與 RAG 消融缺口 ----------
REVIEW_EDITS = [
    ("三個面向皆顯著提升（表一，三項皆介於", "三個面向皆明顯提升（表一，三項皆介於"),
    ("亦均尚未於本文量化評估，留待後續逐項驗證。",
     "亦均尚未於本文量化評估。另，本文之比較以各維度平均分數呈現，未進行統計顯著性檢定，"
     "消融亦未單獨分離 RAG 規則注入之貢獻（所有結果皆於檢索層啟用之配置下取得），"
     "此等統計穩健性與模組級消融之檢驗，連同上列各項，均留待後續逐項驗證。"),
]
for old, new in REVIEW_EDITS:
    print(f"審稿修正 {replace_everywhere(old, new)} 處：{new[:30]}…")

# ---------- 3. 全形標點正規化（1:1 字元映射，按原 run 長度回填） ----------
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

# ---------- 4. 字型：每個含文字之 run 顯式四 slot ----------
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
