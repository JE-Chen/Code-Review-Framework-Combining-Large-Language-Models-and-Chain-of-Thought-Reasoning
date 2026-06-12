"""Produce 論文_v2.2.docx from 論文_v2.1.docx (original untouched): the framework
base model becomes gemma-4-31B-it in prose, and Qwen-series names move INTO the
tables (表二 gains a 基座模型 row, 表六 headers name the evaluated models) so the
quantitative results stay attributed to the configuration that produced them.
Prose outside tables no longer names Qwen; the gemma replay status (no judge
scores yet — no gemma numbers are cited) is recorded in §4.3 / §6.3 / §6.4.1.
One-off helper, mirrors the underscore-prefixed paper/ scripts.
Usage: .venv/Scripts/python.exe paper/_rewrite_paper_v22.py"""
import copy
import re
import sys

from docx import Document
from docx.oxml.ns import qn

sys.stdout.reconfigure(encoding="utf-8")
SRC, DST = "paper/論文_v2.1.docx", "paper/論文_v2.2.docx"
doc = Document(SRC)
body = doc.element.body
W_T, W_P, W_R, W_RPR = qn("w:t"), qn("w:p"), qn("w:r"), qn("w:rPr")
W_TXBX = qn("w:txbxContent")


def paras():
    return body.findall(".//" + W_P)


def para_text(p):
    return "".join(t.text or "" for t in p.findall(".//" + W_T))


def set_text(t, s):
    t.text = s
    if s != s.strip():
        t.set(qn("xml:space"), "preserve")


def in_txbx(p):
    el = p
    while el is not None:
        if el.tag == W_TXBX:
            return True
        el = el.getparent()
    return False


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
    if n == 0:
        raise SystemExit(f"定點改寫未命中：{old[:40]}…")
    return n


# ---------- 1. 表格外散文去 Qwen 化（基底改述為 gemma-4-31B-it） ----------
EDITS = [
    # §3.1.6 推論與訓練
    ("線上推論以本機後端（LocalHF）載入 Qwen3-Coder-30B-A3B(bf16)，掛載微調所得之"
     " LoRA 適配器，並以 SDPA 與雙卡部署降低注意力計算之記憶體峰值",
     "線上推論以本機後端（LocalHF）載入現行基底 gemma-4-31B-it（bf16），掛載微調"
     "所得之 LoRA 適配器，並以 SDPA 注意力核心降低注意力計算之記憶體峰值"),
    ("經 QLoRA 訓練器產出適配器（Adapter output）",
     "經低秩適應訓練器產出適配器（Adapter output）"),
    # 圖二圖說（圖內無模型名，圖說同步去名）
    ("再以 QLoRA 對學生模型 Qwen3-Coder-30B-A3B-Instruct 進行微調",
     "再以低秩適應對學生模型進行微調"),
    # §3.2.1 知識蒸餾流程
    ("本研究的訓練流程採用知識蒸餾與 QLoRA 微調並行的設計",
     "本研究的訓練流程採用知識蒸餾與低秩適應微調並行的設計"),
    ("產出 qwen3_train_data.jsonl，每筆資料包含",
     "產出微調資料集（JSONL 格式），每筆資料包含"),
    ("模型端以 Qwen3-Coder-30B-A3B-Instruct 作為 Student Base Model，搭配"
     " BitsAndBytesConfig（NF4 4-bit + bf16 compute）進行 QLoRA Quantized Load"
     "（prepare_model_for_kbit_training），再透過 LoRA Adapter（r=64、α=64、"
     "dropout=0.1，注入於 q/k/v/o 與 gate/up/down_proj 模組）以 get_peft_model "
     "加入可訓練低秩參數。",
     "模型端以所選基座模型作為 Student Base Model——表二所列之實驗配置搭配"
     " BitsAndBytesConfig（NF4 4-bit + bf16 compute）進行 QLoRA Quantized Load"
     "（prepare_model_for_kbit_training），現行基底 gemma-4-31B-it 則以 bf16 直接"
     "載入——再透過 LoRA Adapter（r=64、α=64、dropout=0.1，注入於注意力與前饋"
     "投影模組）以 get_peft_model 加入可訓練低秩參數。"),
    ("最終輸出為 LoRA Adapter Weights（outputs-lora-qwen3-coder-30b/）",
     "最終輸出為 LoRA Adapter Weights（獨立之適配器權重目錄）"),
    # §3.3 圖一說明（RAG 子流程與三條 Pipeline）
    ("將外部 Rule Documents 透過 Qwen3-Embedding-4B 進行向量化後寫入 FAISS Vector Index",
     "將外部 Rule Documents 透過嵌入模型進行向量化後寫入 FAISS Vector Index"),
    ("三條 Pipeline 共用同一個核心模型 Qwen3-Coder-30B-A3B 並搭載 4-bit "
     "Quantization 與微調得到的 LoRA Adapter，以在有限資源下完成推論。",
     "三條 Pipeline 共用同一個核心模型（現行基底 gemma-4-31B-it，bf16）並搭載"
     "微調得到的 LoRA Adapter，以在有限資源下完成推論。"),
    # §4.3 訓練配置
    ("本研究採用 Qwen3-Coder-30B-A3B-Instruct 模型，並使用 QLoRA 進行微調訓練。",
     "本研究實驗所用之學生模型及其 QLoRA 微調配置如表二所列；框架現行基底為 "
     "gemma-4-31B-it（見 §6.4.1）。"),
    # 表二說明（模型名移入表二首列）
    ("本表呈現以 QLoRA 微調 Qwen3-Coder-30B-A3B-Instruct 時所採用的關鍵超參數實際數值",
     "本表呈現實驗以 QLoRA 微調表列學生模型時所採用的關鍵超參數實際數值"),
    # §5.3.2 結果分析
    ("第一，本研究採用之 Qwen3-Coder-30B 已具備充分之程式碼語義理解能力",
     "第一，表二所列之 30B 級學生模型已具備充分之程式碼語義理解能力"),
    # §5.3.3（模型名移入表六欄名）
    ("Ours-7B 變體（Qwen3 7B 與 Qwen2.5-Coder-7B）", "Ours-7B 變體（表六後二欄）"),
    # §6.3 限制（3）
    ("（3） 微調範圍：本研究僅針對 Qwen3-Coder-30B-A3B-Instruct 進行 QLoRA 微調，"
     "未系統性比較不同基座模型（Qwen2.5-Coder、CodeLlama、StarCoder2）於相同 CoT "
     "框架下之表現；LoRA rank、量化精度（NF4 vs INT8）等超參數消融亦未涵蓋。",
     "（3） 微調範圍：本研究之量化評估僅及於表二所列單一學生模型配置之 QLoRA 微調；"
     "框架基底其後已更換為 gemma-4-31B-it 並於同一基準完成端到端重放，惟其評審評分"
     "尚未執行（見 6.4.1），不同基座模型（CodeLlama、StarCoder2 等）於相同 CoT 框架"
     "下之系統性比較、LoRA rank 與量化精度（NF4 vs INT8）等超參數消融亦未涵蓋。"),
    # 表六欄名補模型名（表內，保留結果歸因）
    ("Ours (30B)", "Ours (Qwen3-Coder-30B)"),
    ("Ours (7B)", "Ours (Qwen3 7B)"),
    ("Ours (coder-7B)", "Ours (Qwen2.5-Coder-7B)"),
]
for old, new in EDITS:
    print(f"改寫 {replace_everywhere(old, new)} 處：{new[:28]}…")

# ---------- 2. §3.2.2 提示詞展示：段內去重，全件去模型名 ----------
_PROBE = "Generate more Qwen3-30B code-review fine-tuning data."
exhibit = next(
    (p for p in paras() if para_text(p).startswith(_PROBE) and not in_txbx(p)),
    None,
)
if exhibit is None:
    raise SystemExit("找不到 §3.2.2 提示詞展示段")
full = para_text(exhibit)
half = full[: len(full) // 2]
if half * 2 == full:
    wts = exhibit.findall(".//" + W_T)
    set_text(wts[0], half)
    for t in wts[1:]:
        set_text(t, "")
    print("提示詞展示：去除段內重複（2 → 1 份）")
print(f"提示詞展示去模型名 {replace_everywhere(_PROBE, 'Generate more code-review fine-tuning data.')} 處（含圖文框）")

# ---------- 3. 表二補「基座模型」列（實驗配置之歸因錨點） ----------
table2 = doc.tables[1]
new_tr = copy.deepcopy(table2.rows[1]._tr)
cells = new_tr.findall(".//" + qn("w:tc"))
for tc, value in zip(cells, ("基座模型", "Qwen3-Coder-30B-A3B-Instruct")):
    wts = tc.findall(".//" + W_T)
    if not wts:
        raise SystemExit("表二模板列缺文字節點")
    set_text(wts[0], value)
    for t in wts[1:]:
        set_text(t, "")
table2.rows[0]._tr.addnext(new_tr)
print("表二：補入基座模型列")

# ---------- 4. §6.4.1 補跨模型重放既成事實段 ----------
anchor = next((p for p in paras() if "偏序對照表" in para_text(p)), None)
if anchor is None:
    raise SystemExit("找不到 6.4.1 偏序對照表段")
new_p = copy.deepcopy(anchor)
nts = new_p.findall(".//" + W_T)
set_text(
    nts[0],
    "此項工作之第一步——以新基座模型重放整條審查管線——已完成：框架現行基底 "
    "gemma-4-31B-it（dense 架構）加掛專屬 LoRA 轉接器（r=64、bf16、僅鎖定語言"
    "模型層），於與第四章完全相同之 44 筆基準資料上，以同一份五步驟提示詞、同一"
    "嵌入索引與檢索閾值 0.7 端到端重放審查管線，逐案產出五步驟輸出與評審提示詞"
    "並隨附歸檔；轉接器訓練之收斂另以前後對照作質性檢核——貪婪解碼下，未掛轉接"
    "器之基礎模型於三題探測題之二退化為重複 token，掛上轉接器後則產出連貫且切題"
    "之審查回答。惟其 CRSCORE++ 與 LLM-as-a-Judge-Our 之評審評分尚未執行，本論文"
    "不引用任何 gemma 系列之分數，表六至表十三之數字均屬表二所列前代學生模型配置"
    "之結果；跨模型之量化比較（含上述品質、成本與延遲之偏序對照）仍屬未來工作。",
)
for t in nts[1:]:
    set_text(t, "")
anchor.addnext(new_p)
print("6.4.1 補入跨模型重放段")

# ---------- 5. 全形標點正規化（1:1 字元映射，按原 run 長度回填） ----------
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

# ---------- 6. 字型：每個含文字之 run 顯式四 slot ----------
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
