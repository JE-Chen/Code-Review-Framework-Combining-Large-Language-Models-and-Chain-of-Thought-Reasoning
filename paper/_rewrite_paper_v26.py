"""Produce 論文_v2.6.docx from 論文_v2.5.docx (original untouched): switch the
CRSCORE++ headline (表六, abstract, §5.2, §5.3) from the GPT-5-judged
Qwen3-Coder-30B numbers to the single-judge (Claude) narrative the author chose.
表六's Ours column now shows gemma-4-31B-it's Claude scores (1.00/0.79/0.86); the
equal same-judge Qwen3-Coder-30B scores (1.00/0.78/0.86) and the judge
disclosures (CRSCORE++ / 7B columns are a different judge; the judge saturates
comprehensiveness) go in an added caption note. Every cited number comes from the
committed score files. One-off helper, mirrors the underscore-prefixed paper/
scripts. Usage: .venv/Scripts/python.exe paper/_rewrite_paper_v26.py"""
import copy
import re
import sys

from docx import Document
from docx.oxml.ns import qn

sys.stdout.reconfigure(encoding="utf-8")
SRC, DST = "paper/論文_v2.5.docx", "paper/論文_v2.6.docx"
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
    else:  # empty cell: append a run+text into first paragraph
        p = cell._tc.find(".//" + W_P)
        r = p.makeelement(W_R, {})
        t = r.makeelement(W_T, {})
        t.text = value
        r.append(t)
        p.append(r)


# ---------- 1. 表六：Ours 欄改為 gemma 之 Claude 分數，其他欄標 † ----------
tbl = None
for t in doc.tables:
    hdr = [c.text.strip() for c in t.rows[0].cells]
    if any("CRSCORE" in h for h in hdr) and any("Qwen3-Coder" in h for h in hdr):
        tbl = t
        break
if tbl is None:
    raise SystemExit("找不到表六（CRSCORE++ 整體評估）")
# header indices
hdrs = [c.text.strip() for c in tbl.rows[0].cells]
i_crs = next(i for i, h in enumerate(hdrs) if "CRSCORE" in h)
i_ours = next(i for i, h in enumerate(hdrs) if "Qwen3-Coder" in h)
i_7b = [i for i, h in enumerate(hdrs) if "7B" in h or "Coder-7" in h or "7b" in h]
# Ours column -> gemma header + Claude values
set_cell(tbl.rows[0].cells[i_ours], "Ours\n(gemma-4-31B-it)")
for r, val in zip((1, 2, 3), ("1.00", "0.79", "0.86")):  # comp / concise / relev
    set_cell(tbl.rows[r].cells[i_ours], val)
# mark different-judge columns with dagger
set_cell(tbl.rows[0].cells[i_crs], hdrs[i_crs].split(chr(10))[0] + " †")
for i in i_7b:
    set_cell(tbl.rows[0].cells[i], hdrs[i] + " †")
print("表六：Ours 欄改 gemma（1.00/0.79/0.86），CRSCORE++ 與 7B 欄標 †")

# ---------- 2. 表六標題後補入 judge 揭露註 ----------
cap = next((p for p in paras() if "表六" in para_text(p)
            and "整體評估" in para_text(p)), None)
if cap is None:
    raise SystemExit("找不到表六標題段")
note = copy.deepcopy(cap)
nts = note.findall(".//" + W_T)
set_text(
    nts[0],
    "註：Ours 欄為 gemma-4-31B-it 之 CRSCORE++ 評分（judge：Claude）；同一 judge "
    "下前代基底 Qwen3-Coder-30B 為完整性 1.00、簡潔性 0.78、相關性 0.86，二者相等。"
    "標 † 之 CRSCORE++ 與 7B 變體欄為不同 judge（分別為原方法與 GPT-5）之參考，"
    "跨欄比較僅供參考；該 judge 對完整性普遍給滿分，故該維度資訊量有限。",
)
for t in nts[1:]:
    set_text(t, "")
cap.addnext(note)
print("表六：補入 judge 揭露註")

# ---------- 3. 摘要（中、英）與 §5.2、§5.3 之同 judge 改寫 ----------
EDITS = [
    # 中文摘要
    ("實驗於 CRSCORE++ 指標上，本框架之完整性、相關性與簡潔性分別達 0.86、0.83 與 "
     "0.64（三者皆以接近 1 為佳），均優於基準之 0.67、0.63 與 0.57，代表審查意見"
     "更少漏看真正該提的問題、且更貼合該次變更。",
     "實驗於 CRSCORE++ 指標上，以同一 judge 評分時，本框架以 gemma-4-31B-it 與"
     "前代學生模型為基底之審查品質相當（完整性／簡潔性／相關性為 "
     "1.00／0.79／0.86 與 1.00／0.78／0.86），且高於 CRSCORE++ 基準（0.67／0.57／"
     "0.63）；惟基準係由不同 judge 評分，且該 judge 對完整性普遍給滿分，故完整性"
     "維度之比較資訊量有限。"),
    # 英文摘要
    ("On the CRSCORE++ metric, the framework attains comprehensiveness, relevance, "
     "and conciseness of 0.86, 0.83, and 0.64, surpassing the baseline's 0.67, "
     "0.63, and 0.57.",
     "On the CRSCORE++ metric, under a single judge the framework is on par with "
     "gemma-4-31B-it and the previous student model as base models "
     "(comprehensiveness/conciseness/relevance 1.00/0.79/0.86 and 1.00/0.78/0.86), "
     "both above the CRSCORE++ baseline (0.67/0.57/0.63); since the baseline was "
     "scored by a different judge that saturates comprehensiveness, the "
     "comprehensiveness comparison is uninformative."),
    # §5.2 RQ1
    ("末看與基準方法之整體對照（對應 RQ1）。由表六之 CRSCORE++ 三維度可知，本研究之 "
     "Ours 配置於comprehensiveness（0.86 vs 0.67）、conciseness（0.64 vs 0.57）與 "
     "relevance（0.83 vs 0.63）三項皆明顯優於 CRSCORE++ 基準（三項均以接近 1 為佳）。"
     "其中完整性之增幅最為明顯，意味本框架之審查意見更少漏看真正",
     "末看與基準方法之整體對照（對應 RQ1）。由表六可知，以同一 judge（Claude）評分時，"
     "本框架以 gemma-4-31B-it 與前代學生模型為基底之 CRSCORE++ 三維度幾乎"
     "相等（1.00／0.79／0.86 對 1.00／0.78／0.86），顯示更換基座未損及審查品質；二者"
     "於簡潔性與相關性均高於 CRSCORE++ 基準（0.57、0.63），惟基準為不同 judge 評分、"
     "且該 judge 對完整性普遍給滿分，故完整性之跨欄差距資訊量有限，更嚴謹之單一 judge "
     "基準比較留待"),
    # §5.3 / 結論
    ("經 CRSCORE++ 與 LLM-as-a-Judge-Our 雙重量化評估並由人工評分交叉驗證，本框架於"
     "完整性、相關性與簡潔性面向均優於基準（表六：0.86 / 0.83 / 0.64 對 0.67 / 0.63 / "
     "0.57）。",
     "經 CRSCORE++ 與 LLM-as-a-Judge-Our 雙重量化評估並由人工評分交叉驗證，於同一 "
     "judge 下本框架以 gemma-4-31B-it 與前代學生模型為基底之審查品質相當"
     "（表六：1.00 / 0.79 / 0.86 對 1.00 / 0.78 / 0.86），且於簡潔性與相關性高於"
     "基準（惟基準為不同 judge、完整性因評審飽和而資訊量有限）。"),
]
for old, new in EDITS:
    replace_once(old, new)
print(f"摘要／§5.2／§5.3 改寫 {len(EDITS)} 處")

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
    # keep ASCII '/' between digits (ratios like 1.00/0.79); only convert CJK-adjacent marks
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
