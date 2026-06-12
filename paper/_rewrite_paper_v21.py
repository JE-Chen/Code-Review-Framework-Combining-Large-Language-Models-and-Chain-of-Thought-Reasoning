"""Produce 論文_v2.1.docx from 論文_v2.0.docx (original untouched), applying the
five paper-author hard rules: full-width punctuation, first-occurrence-only
glosses, 標楷體/Times New Roman run fonts, Chinese-numeral table numbering
(表 2-1 → 表一 cascade), and table-citation fixes whose numbers must match the
cited table. One-off helper, mirrors the underscore-prefixed paper/ scripts.
Usage: .venv/Scripts/python.exe paper/_rewrite_paper_v21.py"""
import copy
import re
import sys

from docx import Document
from docx.oxml.ns import qn

sys.stdout.reconfigure(encoding="utf-8")
SRC, DST = "paper/論文_v2.0.docx", "paper/論文_v2.1.docx"
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
    """Span-aware replace of the first occurrence of old in paragraph p."""
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


def replace_everywhere(old, new):
    if old in new:
        raise SystemExit(f"old 為 new 之子字串，會無窮替換：{old[:40]}…")
    n = 0
    for p in paras():
        while old in para_text(p):
            before = para_text(p)
            replace_once_in_para(p, old, new)
            if para_text(p) == before:
                raise SystemExit(f"替換無進展：{old[:40]}…")
            n += 1
    return n


# ---------- 1. 刪除段落：摘要殘留之 v1.9 舊段、§3.1 佔位圖題 ----------
for anchor in ("特別是在程式碼生成與程式碼審查", "〔請插入附圖〕"):
    hit = next((p for p in paras() if anchor in para_text(p)), None)
    if hit is None:
        raise SystemExit(f"找不到刪除錨點：{anchor}")
    hit.getparent().remove(hit)
    print(f"刪除段落：…{anchor}…")

# ---------- 2. 表號全域平移：表 2-1 改為表一，原表一–表十二 順移為表二–表十三 ----------
SHIFT_SRC = ["表十二", "表十一", "表十", "表九", "表八", "表七",
             "表六", "表五", "表四", "表三", "表二", "表一"]
SHIFT_DST = ["表十三", "表十二", "表十一", "表十", "表九", "表八",
             "表七", "表六", "表五", "表四", "表三", "表二"]
TOKENS = [f"⟦T{i:02d}⟧" for i in range(len(SHIFT_SRC))]
total = 0
for src, tok in zip(SHIFT_SRC, TOKENS):
    total += replace_everywhere(src, tok)
for tok, dst in zip(TOKENS, SHIFT_DST):
    replace_everywhere(tok, dst)
print(f"表號平移：{total} 處")

# ---------- 3. 定點改寫 ----------
EDITS = [
    # 阿拉伯表號殘留 → 中文（新編號）
    ("表 2-1、現有 LLM", "表一、現有 LLM"),
    ("（詳見表 2-1）", "（詳見表一）"),
    ("表 4.4", "表五"),
    ("經 §5.2 表 2 之 LLM 評分消融實驗", "經 §5.2 表七、表八之 LLM 評分消融實驗"),
    ("經 §5.2 表 2 與 §5.1 表 1 比較", "經 §5.2 表十、表十一與 §5.1 表六比較"),
    ("由表 1（CRSCORE++）、表 2（LLM-as-a-Judge-Our 自動評分）與表 3（人工評分）之趨勢可知",
     "由表六（CRSCORE++）、表七至表十一（LLM-as-a-Judge-Our 自動評分）與表十二、表十三（人工評分）之趨勢可知"),
    ("且差距於人工評分（表 3）保持一致方向", "且差距於人工評分（表十二、表十三）保持一致方向"),
    # §5.3.2：原句之 85→95 / 82→98 為 TCSE 表 2 之數字，與本論文表六（85→94、82→90）不符，
    # 且 85/82 欄位為單一提示詞而非基礎模型——逐表改寫為本論文表中真實數值。
    ("表 2 顯示，自基礎模型 → 多階段提示詞（微調 + 多階段）之變化使 Maintainability 由 85 升至 95、"
     "Correctness 由 82 升至 98，表 3 之人工評分亦呈相同方向之提升（Maintainability 79.88 → 86.25、"
     "Correctness 80.75 → 87.75）。相較之下，自「基礎模型 + 多階段（未微調）」→「微調 + 多階段」之變化"
     "於兩表中差距較小（表 2 中 Maintainability 維持 95、Correctness 由 98 持平，表 3 中 Maintainability "
     "由 84.88 升至 86.25、Correctness 由 86.38 升至 87.75）。",
     "表七與表八顯示，自單一提示詞改為多階段提示詞，GPT-5 評分之 Maintainability 由 85 升至 94、"
     "Correctness 由 82 升至 90（表七），Gemini-3 評分之 Maintainability 由 88 升至 95、Correctness "
     "由 95 升至 98（表八），表十二之人工評分亦呈相同方向之提升（Maintainability 由 79.88 升至 86.25、"
     "Correctness 由 80.75 升至 87.75）。相較之下，微調與否之差距於兩類評分中皆較小（表九中 Gemini-3 "
     "評分之 Maintainability 維持 95、Correctness 維持 98，表十三之人工評分 Maintainability 由 84.88 "
     "升至 86.25、Correctness 由 86.38 升至 87.75）。"),
    ("故多階段拆解之邊際貢獻最為顯著（消融中折算約 +34 分",
     "故多階段拆解之邊際貢獻最為顯著（綜合 §5.2 表七至表十三之消融結果折算約 +34 分"),
    ("由表 1 之 CRSCORE++ 三維度可知", "由表六之 CRSCORE++ 三維度可知"),
    ("均優於基準（0.86 / 0.83 / 0.64 對 0.67 / 0.63 / 0.57）",
     "均優於基準（表六：0.86 / 0.83 / 0.64 對 0.67 / 0.63 / 0.57）"),
    # 僅 §6.1 加表號引用，摘要按慣例不引用章節表號（摘要句以「0.57，代表」接續，不會命中）
    ("0.57）。消融分析作為整合框架內部之貢獻分解，顯示多階段提示詞流程",
     "0.57）。消融分析（§5.2 表七至表十三）作為整合框架內部之貢獻分解，顯示多階段提示詞流程"),
    # §3.1 開頭改以圖一引用（圖一題注位於 §3.1 末）
    ("整體架構如下圖(系統架構圖)所示,各層之職責與資料流分述如下。",
     "整體架構如圖一所示，各層之職責與資料流分述如下。"),
    # 重複之中英 gloss（正文首次出現處保留，其後僅以中文名／縮寫稱呼）
    ("程式碼審查（Code Review，由其他開發者或團隊成員檢視並評估程式碼變更之流程）是軟體開發中",
     "程式碼審查是軟體開發中"),
    ("利用大型語言模型（LLM）作為「裁判」", "利用大型語言模型作為「裁判」"),
    ("大型語言模型（Large Language Models, LLMs）的知識蒸餾（Knowledge Distillation）是一種",
     "大型語言模型的知識蒸餾是一種"),
    ("LoRA，全名 Low-Rank Adaptation，是一種", "LoRA 是一種"),
    ("在大型語言模型（LLM）的訓練中，LoRA（Low-Rank Adaptation） 扮演",
     "在大型語言模型的訓練中，LoRA 扮演"),
    ("Hugging Face 的 PEFT（Parameter-Efficient Fine-Tuning）框架", "Hugging Face 的 PEFT 框架"),
    ("知識蒸餾（Knowledge Distillation）與 QLoRA 微調並行", "知識蒸餾與 QLoRA 微調並行"),
    ("提示詞（Prompt）的設計會直接影響", "提示詞的設計會直接影響"),
    ("提示語（prompt）與輸入格式", "提示語與輸入格式"),
    ("下列三項屬於本研究隨附之開源框架（prthinker）之設計貢獻", "下列三項屬於本研究隨附之開源框架之設計貢獻"),
    ("本節描述本研究隨附之開源框架（prthinker）於 §3.1", "本節描述本研究隨附之開源框架於 §3.1"),
    ("本研究隨附之開源框架（prthinker）已將上述審查流程", "本研究隨附之開源框架已將上述審查流程"),
    ("暴露為 MCP（Model Context Protocol）工具", "暴露為 MCP 工具"),
    # §3.1 原文為半形括號之重複 gloss（prthinker 首次於 §1.5、RAG 首次於 §2.6）
    ("隨附開源框架(prthinker)於上述核心之外", "隨附開源框架於上述核心之外"),
    ("以檢索增強生成(Retrieval-Augmented Generation, RAG)取得外部知識", "以檢索增強生成取得外部知識"),
    # QLoRA 摘要首次出現補英文原名（正文 §2.8 已有完整定義）
    ("結合量化低秩適應（QLoRA）將大型教師模型",
     "結合量化低秩適應（Quantized Low-Rank Adaptation, QLoRA）將大型教師模型"),
    # 審稿意見：無統計檢定不稱「顯著」（RQ1 題目措辭屬凍結事實，不動）
    ("三項皆顯著優於 CRSCORE++ 基準", "三項皆明顯優於 CRSCORE++ 基準"),
    # 半形冒號、「鍊」錯字、LLM-as -a 斷字
    ("關鍵字: 大型語言模型、程式碼審查、思維鍊推理", "關鍵字：大型語言模型、程式碼審查、思維鏈推理"),
    ("LLM-as -a-Judge-Our", "LLM-as-a-Judge-Our"),
]
for old, new in EDITS:
    n = replace_everywhere(old, new)
    if n == 0:
        raise SystemExit(f"定點改寫未命中：{old[:40]}…")
    print(f"改寫 {n} 處：{old[:28]}…")

# ---------- 3b. §6.3 限制補（5）：統計檢定與 RAG 消融範圍（審稿意見之誠實回應） ----------
lim4 = next((p for p in paras() if "部署面實證" in para_text(p)), None)
if lim4 is None:
    raise SystemExit("找不到 6.3（4）段")
lim5 = copy.deepcopy(lim4)
l5ts = lim5.findall(".//" + W_T)
set_text(l5ts[0],
         "（5） 統計檢定與模組消融範圍：本研究之比較以各維度平均分數呈現，受限於 44 筆樣本規模，"
         "未進行統計顯著性檢定（如成對樣本之無母數檢定），各表分數差異之統計穩健性尚待更大樣本下確認。"
         "消融實驗亦僅分離多階段提示詞與模型微調二者之貢獻，RAG 規則注入未單獨消融，"
         "§5 所載結果皆於檢索層啟用之配置下取得。")
for t in l5ts[1:]:
    set_text(t, "")
lim4.addnext(lim5)
print("6.3 補入（5）統計檢定與模組消融範圍")

# ---------- 4. 表次目錄補入新表一 ----------
# 主目錄為未填值之 TOC 欄位，docx 內無頁碼可引；頁碼留空，待 Word 重新分頁後填入。
toc_target = next(
    (p for p in paras()
     if para_text(p).startswith("表二、模型訓練參數配置") and re.search(r"\d+$", para_text(p))),
    None)
if toc_target is not None:
    clone = copy.deepcopy(toc_target)
    cts = clone.findall(".//" + W_T)
    set_text(cts[0], "表一、現有 LLM 程式碼審查方法之比較與研究缺口對照")
    for t in cts[1:]:
        set_text(t, "")
    toc_target.addprevious(clone)
    print("表次目錄補入表一（頁碼留空，待 Word 更新欄位）")
else:
    print("警告：表次目錄未補入（找不到表二條目）")

# ---------- 5. 全形標點正規化（1:1 字元映射，逐段按原 run 長度回填） ----------
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

# ---------- 6. 字型：每個含文字之 run 顯式四 slot（中文標楷體、英文 Times New Roman） ----------
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
