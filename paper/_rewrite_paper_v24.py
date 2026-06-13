"""Produce 論文_v2.4.docx from 論文_v2.3.docx (original untouched): add one
consolidated statement that the framework reviews an ENTIRE Pull Request
end-to-end (per-file CoT chained across changed files → inline findings +
a PR-level summary comment + a JudgeStep merge-gate verdict, integrated into
GitHub Actions CI), framed as an engineering contribution with its real-PR
effectiveness marked as future work. No empirical number, table, RQ, or
reference is changed; the new paragraph carries no fabricated PR-level result.
One-off helper, mirrors the underscore-prefixed paper/ scripts.
Usage: .venv/Scripts/python.exe paper/_rewrite_paper_v24.py"""
import copy
import re
import sys

from docx import Document
from docx.oxml.ns import qn

sys.stdout.reconfigure(encoding="utf-8")
SRC, DST = "paper/論文_v2.3.docx", "paper/論文_v2.4.docx"
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


# ---------- 1. §3.4 末新增「整份 PR 端到端審查」之能力與貢獻段 ----------
_WHOLE_PR = (
    "於整份 Pull Request 之層級，框架將上述逐檔之多階段審查串接為端到端之 "
    "PR 審查：對 PR 內各變更檔分別執行五階段 CoT，彙整為標註於 diff 上之行內 "
    "finding（inline findings）與一則 PR 級摘要留言，並由 JudgeStep 以保守聚合"
    "規則裁決為 APPROVE / REQUEST_CHANGES / COMMENT 之合併閘門，整體整合於 "
    "GitHub Actions CI 並於 Pull Request 事件自動觸發。此一對整份 PR 之端到端"
    "審查為本框架之工程貢獻；惟其於真實 PR 流量上之缺陷攔截率、作者採納率與"
    "審查延遲等效益本論文未予評估，列為 §6.4 之未來工作。"
)
anchor = next(
    (p for p in paras()
     if "三條 Pipeline 共用同一個核心模型" in para_text(p)),
    None,
)
if anchor is None:
    raise SystemExit("找不到 §3.4 結尾錨點段")
new_p = copy.deepcopy(anchor)
nts = new_p.findall(".//" + W_T)
set_text(nts[0], _WHOLE_PR)
for t in nts[1:]:
    set_text(t, "")
anchor.addnext(new_p)
print("§3.4 末補入整份 PR 端到端審查段")

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
