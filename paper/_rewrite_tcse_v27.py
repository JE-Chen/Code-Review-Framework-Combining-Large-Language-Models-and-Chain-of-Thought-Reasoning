"""Produce TCSE_v2.7.docx from TCSE_v2.6.docx (original untouched), applying
the five paper-author hard rules: Chinese-numeral figure/table numbering
(圖 1 → 圖一 etc.), full-width punctuation in Chinese captions, explicit
標楷體/Times New Roman run fonts, and table citations for result claims.
One-off helper, mirrors the underscore-prefixed paper/ scripts.
Usage: .venv/Scripts/python.exe paper/_rewrite_tcse_v27.py"""
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
    end = idx + len(old)
    first = True
    for a, b, t in spans:
        if b <= idx or a >= end:
            continue
        seg = t.text or ""
        lo, hi = max(idx - a, 0), min(end - a, len(seg))
        set_text(t, seg[:lo] + (new if first else "") + seg[hi:])
        first = False
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

# ---------- 3. 全形標點正規化（1:1 字元映射，按原 run 長度回填） ----------
PUNCT_MAP = {",": "，", ";": "，", ":": "：", "?": "？", "!": "！"}


def _cjkish(ch):
    return ("一" <= ch <= "鿿" or "　" <= ch <= "〿"
            or "＀" <= ch <= "￯" or ch in "—…•")


def convert_punct(text):
    chars = list(text)
    stack = []
    for i, ch in enumerate(chars):
        if ch == "(":
            stack.append(i)
        elif ch == ")" and stack:
            j = stack.pop()
            seg = text[j + 1:i]
            prev = next((c for c in reversed(text[:j]) if c != " "), "")
            nxt = next((c for c in text[i + 1:] if c != " "), "")
            if (any(_cjkish(c) for c in seg) or (prev and _cjkish(prev))
                    or (nxt and _cjkish(nxt))):
                chars[j], chars[i] = "（", "）"
    for i, ch in enumerate(chars):
        if ch in PUNCT_MAP:
            prev = next((c for c in reversed(chars[:i]) if c != " "), "")
            nxt = next((c for c in chars[i + 1:] if c != " "), "")
            if _cjkish(prev) or _cjkish(nxt):
                chars[i] = PUNCT_MAP[ch]
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
