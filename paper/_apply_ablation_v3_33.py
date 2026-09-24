"""Add the retrieval / fine-tuning ablation section to the thesis.

Reads 論文_v3.32.docx (never modified) and writes 論文_v3.33.docx. Two changes
only, everything else in v3.32 is left byte-identical:

  A. new §5.4「檢索與微調之消融分析」at the end of chapter 5 (after the §5.3.3
     closing paragraph, before 第六章), carrying 表十一 (five paired ablation
     comparisons) and 表十二 (judge re-scoring drift), plus the prose that
     frames both tables conservatively.
  B. two new §6.3 limitations, （9） judge scoring stability and （10） the
     retrieval / fine-tuning effects not being empirically supported.

Every number is transcribed from datas/Research_Data/EXPERIMENT_RESULTS_TABLES.md
§四–§十 (the authoritative aggregate), which in turn is backed by
datas/Results/judge_session_robustness_20260727.md and the per-case score files:

  表十一 rows 1–5  = EXPERIMENT_RESULTS_TABLES §五, §六, §七, §八, §九
                     (成對平均差, n=44 each; 表內 Holm 校正 p 不入表格，改由
                      說明段落交代範圍 0.106–1.000、唯一例外 0.012 與校正程序)
  表十二 row 1     = same-day ~12h re-judge of the un-adapted base model
                     rag_off arm, means over its 44 cases
                     (−0.02 / −0.02 / +0.52 / −0.25 / +0.27, matches the
                     「同日相隔約 12 小時 … 變動皆在 ±0.52 以內」claim in §四)
  表十二 row 2     = §四 的隔日重判 (+1.02 / +2.68 / +2.84 / +9.23 / +4.66)
  檢索命中 25／44、每案 3.02 份 = §三 (0.32 校準閾值) 與 §六 註
  裁判場次雜訊約 3 分            = §四 與 §十
  掛載 LoRA 輸出短約 16%         = §九 註

The source file labels the multi-day re-judge as「2026-07-22 評分與 2026-07-26
重判」(≈5 天，四個日曆日)，故表十二只寫「相隔數日」，不寫任何未經該檔支持的天數。

Table/figure numbering stays in Chinese numerals, the 主目錄 gains a 5.4 entry
and the 表次目錄 gains the two matching entries (SEQ + PAGEREF fields are kept
live, each pointing at a freshly created bookmark, so Word renumbers and
re-paginates on a field update), and fonts are normalised to the four-slot
rFonts at the end. The 主目錄 lives inside a `w:sdt` block, so it is reached
through the sdtContent element rather than doc.paragraphs.

Usage: .venv/Scripts/python.exe paper/_apply_ablation_v3_33.py
"""
import copy
import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt
from docx.table import Table
from docx.text.paragraph import Paragraph

sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(__file__).parent
SRC = BASE / "論文_v3.32.docx"
DST = BASE / "論文_v3.33.docx"

LATIN = "Times New Roman"
EAST_ASIA = "標楷體"
LABEL_W, VALUE_W = 2300, 1200          # dxa; 2300 + 5*1200 = 8300 = text width


# --------------------------------------------------------------------------- #
# low-level helpers (same shape as _apply_paper.py / _rewrite_v3_9_data.py)
# --------------------------------------------------------------------------- #
def set_run_fonts(run_el):
    rpr = run_el.get_or_add_rPr()
    rfonts = rpr.get_or_add_rFonts()
    for slot in ("w:ascii", "w:hAnsi", "w:cs"):
        rfonts.set(qn(slot), LATIN)
    rfonts.set(qn("w:eastAsia"), EAST_ASIA)
    if rfonts.get(qn("w:hint")) is not None:
        del rfonts.attrib[qn("w:hint")]


def is_tof(p):
    return "table of figures" in (p.style.name or "").lower()


def find_body_para(doc, anchor, exact=False):
    hits = []
    for p in doc.paragraphs:
        if is_tof(p):
            continue
        text = p.text.strip()
        if (text == anchor) if exact else (anchor in p.text):
            hits.append(p)
    if len(hits) != 1:
        raise SystemExit(f"BODY ANCHOR not unique ({len(hits)}): {anchor[:44]}")
    return hits[0]


def para_fmt(p):
    ppr = p._p.find(qn("w:pPr"))
    rpr = None
    for r in p.runs:
        if r.text.strip():
            rpr = r._element.find(qn("w:rPr"))
            break
    return (copy.deepcopy(ppr) if ppr is not None else None,
            copy.deepcopy(rpr) if rpr is not None else None)


def make_para_like(after_el, parent, fmt, text):
    ppr, rpr = fmt
    new_p = OxmlElement("w:p")
    after_el.addnext(new_p)
    if ppr is not None:
        new_p.append(copy.deepcopy(ppr))
    para = Paragraph(new_p, parent)
    run = para.add_run(text)
    if rpr is not None:
        run._element.insert(0, copy.deepcopy(rpr))
    set_run_fonts(run._element)
    return new_p


# --------------------------------------------------------------------------- #
# caption (SEQ 表格 \* DBNUM1) + 表次目錄 entry
# --------------------------------------------------------------------------- #
def next_bookmark_id(doc):
    ids = [int(b.get(qn("w:id")))
           for b in doc.element.body.iter(qn("w:bookmarkStart"))
           if (b.get(qn("w:id")) or "").isdigit()]
    return max(ids) + 1 if ids else 1


def add_bookmark(p_el, name, bm_id):
    """Wrap a paragraph in a Word bookmark so 目錄 entries can hyperlink to it
    (mirrors how the live 5.3 heading carries _Toc235644083)."""
    start = OxmlElement("w:bookmarkStart")
    start.set(qn("w:id"), str(bm_id))
    start.set(qn("w:name"), name)
    end = OxmlElement("w:bookmarkEnd")
    end.set(qn("w:id"), str(bm_id))
    ppr = p_el.find(qn("w:pPr"))
    if ppr is not None:
        ppr.addnext(start)
    else:
        p_el.insert(0, start)
    p_el.append(end)
    print(f"OK bookmark {name}")


def make_caption(after_el, tmpl_p, numeral, title, bm_name, bm_id):
    """Clone a live caption paragraph so the SEQ field and the bookmark that the
    表次目錄 hyperlinks to both survive, then retitle it."""
    new_p = copy.deepcopy(tmpl_p._p)
    after_el.addnext(new_p)
    for tag, attr in ((qn("w:bookmarkStart"), True), (qn("w:bookmarkEnd"), False)):
        el = new_p.find(tag)
        if el is None:
            raise SystemExit("caption template lost its bookmark")
        el.set(qn("w:id"), str(bm_id))
        if attr:
            el.set(qn("w:name"), bm_name)

    state, tail_runs = 0, []
    for r in new_p.findall(qn("w:r")):
        fld = r.find(qn("w:fldChar"))
        if fld is not None:
            kind = fld.get(qn("w:fldCharType"))
            if kind == "separate":
                state = 1
                continue
            if kind == "end":
                state = 2
                continue
        if state == 1:                       # cached SEQ result (表「十」)
            wt = r.find(qn("w:t"))
            if wt is not None:
                wt.text = numeral
                set_run_fonts(r)
        elif state == 2:                     # 、 + caption title
            tail_runs.append(r)
    if not tail_runs:
        raise SystemExit("caption template lost its title runs")
    head = tail_runs[0]
    wt = head.find(qn("w:t"))
    wt.text = "、" + title
    wt.set(qn("xml:space"), "preserve")
    set_run_fonts(head)
    for r in tail_runs[1:]:
        r.getparent().remove(r)
    print(f"OK caption 表{numeral}、{title}")
    return new_p


def _entry_caption(p):
    return p.text.split("\t")[0].strip()


def find_tof(doc, caption):
    hits = [p for p in doc.paragraphs
            if is_tof(p) and _entry_caption(p) == caption]
    if len(hits) != 1:
        raise SystemExit(f"TOF not unique ({len(hits)}): {caption}")
    return hits[0]


def clone_entry(tmpl_el, after_el, caption, bm_name, page=None):
    """Clone a cached 目錄／表次目錄 entry, retitle it, and repoint its
    hyperlink anchor and PAGEREF field at bm_name (page number stays cached
    until Word refreshes fields)."""
    clone = copy.deepcopy(tmpl_el)
    after_el.addnext(clone)
    texts = list(clone.iter(qn("w:t")))
    if len(texts) < 2:
        raise SystemExit(f"entry template too few w:t: {caption}")
    texts[0].text = caption
    texts[0].set(qn("xml:space"), "preserve")
    for t in texts[1:-1]:
        t.text = ""
    if page is not None:
        texts[-1].text = page
    for r in clone.findall(".//" + qn("w:r")):
        if r.find(qn("w:t")) is not None:
            set_run_fonts(r)
    hyperlink = clone.find(qn("w:hyperlink"))
    if hyperlink is not None:
        hyperlink.set(qn("w:anchor"), bm_name)
    for instr in clone.iter(qn("w:instrText")):
        if instr.text and "PAGEREF" in instr.text:
            instr.text = f" PAGEREF {bm_name} \\h "
    return clone


def toc_entries(doc):
    """Main 目錄 paragraphs, which sit inside a w:sdt and are therefore invisible
    to doc.paragraphs (and to _dump_docx.py)."""
    sdt = doc.element.body.find(qn("w:sdt"))
    if sdt is None:
        raise SystemExit("main 目錄 sdt not found")
    content = sdt.find(qn("w:sdtContent"))
    return [(p, Paragraph(p, doc).text) for p in content.findall(qn("w:p"))]


def find_toc_entry(doc, caption):
    hits = [p for p, text in toc_entries(doc) if text.split("\t")[0].strip() == caption]
    if len(hits) != 1:
        raise SystemExit(f"目錄 entry not unique ({len(hits)}): {caption}")
    return hits[0]


# --------------------------------------------------------------------------- #
# table construction
# --------------------------------------------------------------------------- #
def _set_cell(cell, text, bold):
    for extra in cell.paragraphs[1:]:
        extra._p.getparent().remove(extra._p)
    p = cell.paragraphs[0]
    for r in list(p.runs):
        r._element.getparent().remove(r._element)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    set_run_fonts(run._element)
    run.font.size = Pt(12)
    run.bold = bold or None


def _resize_rows(tbl, n_target):
    while len(tbl.rows) > n_target:
        tr = tbl.rows[-1]._tr
        tr.getparent().remove(tr)
    while len(tbl.rows) < n_target:
        last_tr = tbl.rows[-1]._tr
        new_tr = copy.deepcopy(last_tr)
        last_tr.addnext(new_tr)


def _set_widths(tbl, widths):
    grid = tbl._tbl.find(qn("w:tblGrid"))
    for col, width in zip(grid.findall(qn("w:gridCol")), widths):
        col.set(qn("w:w"), str(width))
    for row in tbl.rows:
        for cell, width in zip(row.cells, widths):
            tcpr = cell._tc.get_or_add_tcPr()
            tcw = tcpr.find(qn("w:tcW"))
            if tcw is None:
                tcw = OxmlElement("w:tcW")
                tcpr.append(tcw)
            tcw.set(qn("w:w"), str(width))
            tcw.set(qn("w:type"), "dxa")


def insert_table(after_el, parent, tmpl_tbl_el, rows, widths):
    new_tbl = copy.deepcopy(tmpl_tbl_el)
    after_el.addnext(new_tbl)
    tbl = Table(new_tbl, parent)
    _resize_rows(tbl, len(rows))
    _set_widths(tbl, widths)
    for i, values in enumerate(rows):
        cells = tbl.rows[i].cells
        if len(values) != len(cells):
            raise SystemExit(f"row {i} has {len(values)} cells, table has {len(cells)}")
        for cell, value in zip(cells, values):
            _set_cell(cell, value, bold=(i == 0))
    print(f"OK table {len(rows)}x{len(rows[0])}")
    return new_tbl


def normalise_fonts(doc):
    has_content = re.compile(r"[A-Za-z0-9一-鿿　-〿＀-￯]")
    fixed = 0
    for r in doc.element.body.findall(".//" + qn("w:r")):
        text = "".join(t.text or "" for t in r.findall(qn("w:t")))
        if not text or not has_content.search(text):
            continue
        rpr = r.find(qn("w:rPr"))
        rfonts = rpr.find(qn("w:rFonts")) if rpr is not None else None
        if rfonts is not None and rfonts.get(qn("w:ascii")) == "Cambria Math":
            continue
        if rpr is None:
            rpr = r.makeelement(qn("w:rPr"), {})
            r.insert(0, rpr)
        if rfonts is None:
            rfonts = rpr.makeelement(qn("w:rFonts"), {})
            rpr.insert(0, rfonts)
        for slot in ("w:ascii", "w:hAnsi", "w:cs"):
            rfonts.set(qn(slot), LATIN)
        rfonts.set(qn("w:eastAsia"), EAST_ASIA)
        fixed += 1
    print(f"OK fonts normalised on {fixed} runs")


# --------------------------------------------------------------------------- #
# content (numbers traceable to EXPERIMENT_RESULTS_TABLES.md §四–§十)
# --------------------------------------------------------------------------- #
HEADING = "5.4 檢索與微調之消融分析"

S54_SCOPE = (
    "§5.3 的對照集中於多階段流程與單一提示詞，尚未回答另一組設計問題：規則脈絡的供給"
    "方式與模型微調，是否各自對審查文字的主觀品質產生可測得的影響。本節以五項成對比較"
    "補充此一缺口。五項比較均以 §4.1 的 44 筆基準（統計見表二）為受測案例，同一案例在兩種條件下各"
    "生成一份審查文字，再依 §4.2 所述五個百分制維度由自動裁判評分，成對樣本數均為 44 對。"
)

S54_PROTOCOL = (
    "評分程序另加入一項控制。本研究觀察到自動裁判在不同評分場次之間會出現整體漂移，"
    "因此每份審查文字均由自動裁判於兩個獨立評分場次各評一次後取平均，每一場次評分 "
    "352 案，且成對比較之兩組均於同一評分場次完成評分，使場次因素在配對內相互抵消。"
    "統計檢定採雙尾 Wilcoxon 符號等級檢定，此法不假設分數呈常態分布，只依成對差的正負與大小"
    "排序判斷，並以 Holm 法校正五次檢定，逐步提高判定門檻，以免同時檢視五個維度時將"
    "偶然波動誤認為真實差異。"
)

CAP11_TITLE = "檢索規則供給與微調之五項成對比較"
CAP11_FULL = "表十一、" + CAP11_TITLE
ROWS11 = [
    ["比較條件", "可讀性", "建設性", "正確性", "涵蓋度", "完整性"],
    ["相關規則檢索減停用檢索（掛載 LoRA 部署）",
     "−0.25", "−0.56", "−0.92", "−1.42", "−1.10"],
    ["相關規則檢索減停用檢索（未掛載 LoRA 基礎模型）",
     "−0.25", "−0.10", "−1.12", "−0.35", "−0.66"],
    ["注入三條無關規則減停用檢索基準",
     "−0.18", "−0.15", "+0.98", "−0.11", "−0.15"],
    ["直接注入全部十九條相關規則減停用檢索基準",
     "−0.66", "−0.49", "−1.05", "−1.19", "−1.20"],
    ["掛載 LoRA 減未掛載 LoRA 基礎模型（檢索關閉）",
     "+0.00", "−0.30", "−0.53", "−1.05", "−0.52"],
]
# Holm p 值不入表：校正後 p 有 1.000 上限且被迫單調，表內會出現大量重複值而妨礙判讀，
# 故僅於說明段落以一句話交代其範圍、唯一例外與校正程序（資訊不減，只是換位置）。
DESC11 = (
    "表十一列出五項成對比較在五個維度上的成對平均差，數值為前一條件減後一條件，負值"
    "代表前一條件得分較低，各項的成對樣本數均為 44 對。五項比較依序為相關規則檢索相對"
    "停用檢索（掛載 LoRA 部署）、相關規則檢索相對停用檢索（未掛載 LoRA 的基礎模型）、"
    "注入三條無關規則相對停用檢索基準、直接注入全部十九條相關規則相對停用檢索基準，"
    "以及掛載 LoRA 相對未掛載 LoRA 的基礎模型（檢索關閉）。統計判定以同一項比較的五個"
    "維度為校正家族，除直接注入全部十九條相關規則一項於可讀性維度的 Holm 校正後 p 為 "
    "0.012 外，其餘二十四個維度檢定的 Holm 校正後 p 值介於 0.106 至 1.000，均未達顯著。"
    "Holm 校正採逐步向下程序，依未校正 p 值由小至大逐一調整，校正後的 p 值以 1.000 為"
    "上限並沿此順序維持單調不減，故不同維度常落在相同的校正後數值。"
)

S54_MAIN = (
    "如表十一所示，五項比較合計二十五個維度檢定，其中二十四項未達校正後統計顯著，且"
    "所有成對平均差的絕對值皆不超過 1.42 分。就本 44 案合成 Python 基準而言，四種規則"
    "供給路徑（經檢索取得相關規則、注入無關規則、直接注入全部相關規則，以及在有無微調"
    "兩種部署下的檢索）與微調本身，均未產生可測得的品質提升。"
)

S54_EXCEPTION = (
    "唯一的例外出現在直接注入全部十九條相關規則的一組。如表十一所示，該組可讀性的成對"
    "平均差為 −0.66 分，Holm 校正後的 p 為 0.012。本研究將其列為邊緣觀察而非發現：若改"
    "以五項比較合計二十五次檢定為單一家族施以 Holm 校正，該項校正後的 p 為 0.060，未達"
    "顯著。此一方向是否穩定，需增加評分場次或擴大樣本方能定論。"
)

S54_RETRIEVAL = (
    "上述結果不能歸因於檢索未觸發。在啟用相關規則檢索的條件下，44 案中有 25 案至少取回"
    "一份規則文件，全體平均每案取回 3.02 份，可確認規則內容確實進入提示詞，未達顯著並非"
    "因為檢索完全沒有作動。"
)

CAP12_TITLE = "同一批審查文字於不同評分場次重判之分數變動"
CAP12_FULL = "表十二、" + CAP12_TITLE
ROWS12 = [
    ["重判間隔", "可讀性", "建設性", "正確性", "涵蓋度", "完整性"],
    ["同日相隔約十二小時", "−0.02", "−0.02", "+0.52", "−0.25", "+0.27"],
    ["相隔數日", "+1.02", "+2.68", "+2.84", "+9.23", "+4.66"],
]
DESC12 = (
    "表十二取同一批 44 案的審查文字，於不同時間點交由同一自動裁判重新評分，列出五個"
    "維度的成對平均分數變動，正值代表後一次評分給分較高。兩次評分之間審查文字完全未變，"
    "故表中差異全部來自評分場次本身。"
)

S54_RESOLUTION = (
    "表十二用於界定可辨識效果量的下限。如表十二所示，同日相隔約十二小時的重判，五個維度"
    "的變動皆在 0.52 分以內，相隔數日的重判則五個維度全數上移，其中涵蓋度變動達 9.23 分。"
    "就同一項比較在兩個評分場次分別計算成對平均差，其變動幅度最大可達約 3 分，因此小於"
    "此幅度的差異無法與評分場次雜訊區分。表十一各項成對平均差的絕對值皆不超過 1.42 分，"
    "全部落在此一雜訊幅度之內。"
)

S54_LENGTH = (
    "掛載 LoRA 的一組另有一項本研究資料無法分辨的解讀。該組的審查輸出平均較未掛載 LoRA 的"
    "基礎模型短約 16%，而涵蓋度與完整性兩個維度本質上偏好較詳盡的輸出。表十一中該組於"
    "涵蓋度與完整性的負向差值，既可能反映微調使輸出較為簡潔，也可能反映微調使涵蓋度略降，"
    "本研究資料無法區分此二種解讀，輸出長度與品質維度的關係亦未於本輪實驗中加以控制。"
)

S54_CLOSE = (
    "綜合本節，五項比較均未觀察到規則脈絡供給方式或微調對五項主觀品質維度的可測得影響。"
    "此處僅能陳述未觀察到差異，並不等於證明各條件之間相同，本研究未進行等價檢定，亦未"
    "預先設定等價界限，相關限制列於 §6.3。"
)

LIM9 = (
    "（9）自動裁判之評分穩定性：本研究所用之自動裁判在不同評分場次之間會出現整體漂移。"
    "同一批審查文字於相隔數日的兩次評分之間，五個維度分數整體上移，其中涵蓋度最大變動"
    "達 9.23 分（見表十二）。§5.4 因此改採兩個評分場次的平均，並要求成對比較之兩組於"
    "同一評分場次完成評分，惟此程序只能降低而非消除場次影響，本研究可辨識的最小效果量"
    "因而受限於約 3 分。"
)

LIM10 = (
    "（10）檢索與微調之獨立效果未獲實證支持：§5.4 的五項消融比較均未觀察到可測得的品質"
    "差異（見表十一），故本研究不宣稱檢索增強或微調對五項主觀品質維度具有提升作用。此"
    "為未觀察到差異，並不等於證明兩者相同，本研究未進行等價檢定，亦未預先設定等價界限，"
    "該項驗證列為後續工作。"
)


# --------------------------------------------------------------------------- #
def main():
    doc = Document(SRC)
    parent = doc.paragraphs[0]._parent

    heading_fmt = para_fmt(find_body_para(doc, "5.3 結果分析", exact=True))
    body_fmt = para_fmt(find_body_para(doc, "其次比較多階段流程與單一提示詞"))
    desc_fmt = para_fmt(find_body_para(doc, "本表為前代 Qwen 學生模型組態之人工評分結果"))
    lim_fmt = para_fmt(find_body_para(doc, "（3）微調組態適用範圍"))
    cap_tmpl = find_body_para(
        doc, "表十、前代 Qwen 組態之人工評分：微調與未微調比較", exact=True)
    tbl_tmpl = copy.deepcopy(doc.tables[0]._element)      # 表一：6 欄，可容納六欄新表
    toc_tmpl = copy.deepcopy(find_toc_entry(doc, "5.3 結果分析"))   # 目錄 level-2 樣式 21
    bm_id = next_bookmark_id(doc)
    bm54, bm11, bm12 = "_Toc235644149", "_Toc235644150", "_Toc235644151"

    # ---- A. §5.4 at the end of chapter 5 ---------------------------------- #
    cursor = find_body_para(doc, "綜合 §5.3.1 至 §5.3.3")._p
    cursor = make_para_like(cursor, parent, heading_fmt, HEADING)
    add_bookmark(cursor, bm54, bm_id + 2)
    print(f"OK heading {HEADING}")
    cursor = make_para_like(cursor, parent, body_fmt, S54_SCOPE)
    cursor = make_para_like(cursor, parent, body_fmt, S54_PROTOCOL)

    cursor = make_caption(cursor, cap_tmpl, "十一", CAP11_TITLE, bm11, bm_id)
    cursor = insert_table(cursor, parent, tbl_tmpl, ROWS11,
                          [LABEL_W] + [VALUE_W] * 5)
    cursor = make_para_like(cursor, parent, desc_fmt, DESC11)
    cursor = make_para_like(cursor, parent, body_fmt, S54_MAIN)
    cursor = make_para_like(cursor, parent, body_fmt, S54_EXCEPTION)
    cursor = make_para_like(cursor, parent, body_fmt, S54_RETRIEVAL)

    cursor = make_caption(cursor, cap_tmpl, "十二", CAP12_TITLE, bm12, bm_id + 1)
    cursor = insert_table(cursor, parent, tbl_tmpl, ROWS12,
                          [LABEL_W] + [VALUE_W] * 5)
    cursor = make_para_like(cursor, parent, desc_fmt, DESC12)
    cursor = make_para_like(cursor, parent, body_fmt, S54_RESOLUTION)
    cursor = make_para_like(cursor, parent, body_fmt, S54_LENGTH)
    make_para_like(cursor, parent, body_fmt, S54_CLOSE)

    # ---- B. §6.3 limitations （9）（10） ----------------------------------- #
    lim_anchor = find_body_para(doc, "（8）訓練設定與評估範圍")._p
    lim9 = make_para_like(lim_anchor, parent, lim_fmt, LIM9)
    make_para_like(lim9, parent, lim_fmt, LIM10)
    print("OK §6.3 +（9）+（10）")

    # ---- C. 表次目錄 ------------------------------------------------------ #
    ref = find_tof(doc, "表十、前代 Qwen 組態之人工評分：微調與未微調比較")._p
    ref = clone_entry(ref, ref, CAP11_FULL, bm11)
    print(f"OK 表次目錄 +{CAP11_FULL[:12]}")
    clone_entry(ref, ref, CAP12_FULL, bm12)
    print(f"OK 表次目錄 +{CAP12_FULL[:12]}")

    # ---- D. 主目錄（w:sdt 內）：5.4 排在 5.3.3 之後、第六章之前 ------------ #
    after = find_toc_entry(doc, "5.3.3 與基準方法（CRSCORE++）之對照")
    page = Paragraph(after, doc).text.split("\t")[-1].strip()   # 沿用鄰近條目頁碼
    clone_entry(toc_tmpl, after, HEADING, bm54, page=page)
    print(f"OK 目錄 +{HEADING}（快取頁碼 {page}）")

    normalise_fonts(doc)
    doc.save(DST)
    print(f"SAVED {DST.name}")


if __name__ == "__main__":
    main()
