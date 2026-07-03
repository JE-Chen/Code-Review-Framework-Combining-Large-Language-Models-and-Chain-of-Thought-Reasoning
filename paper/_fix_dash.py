"""Remove the prose 破折號 (em-dash 「—」/「——」, box-drawing 「──」, horizontal
bar 「―」) from a paper .docx, per REWRITE_BRIEF §1.3 「子句以『，』連接」. The
破折號 reads as AI-generated em-dash overuse and joins clauses ambiguously
(the same failure mode the full-width-semicolon rule guards against), so every
prose break is replaced with proper full-width punctuation 「，」 or 「：」.

Boundary this guards: ONLY the typographic dash used as a sentence break is
touched. The following dash-shaped tokens are NOT 破折號 and are preserved —
  * CLI flags / option syntax            e.g. --redact-secrets, git log --since
  * HTML comment markers                 e.g. <!-- prthinker:summary -->
  * en-dash number / section / cite ranges  e.g. 1–5 分, §3.3.2–§3.3.9, [1]–[22]
  * the minus sign in badges             e.g. +a −b
These use U+002D / U+2013 / U+2212, never U+2014 / U+2500 / U+2015, so the
codepoint filter below excludes them automatically.

Each CJK 破折號 sits in its own <w:t> run, so the run is replaced in place and
fonts / tables / images are untouched. Replacements are keyed by a unique
paragraph anchor (not a fragile global index) and the per-paragraph dash count
is asserted, so a miscount aborts instead of silently corrupting the text. The
English-abstract paragraph carries its em-dashes inside a longer run, handled
separately by an in-run string replace. One-off helper, mirrors the
underscore-prefixed paper/ scripts.

Usage: .venv/Scripts/python.exe paper/_fix_dash.py <in.docx> <out.docx>
"""
import sys

from docx import Document

sys.stdout.reconfigure(encoding="utf-8")
src, dst = sys.argv[1], sys.argv[2]
doc = Document(src)

DASH_CHARS = {"—", "─", "―"}  # — em-dash, ─ box-h, ― bar
CLAUSE_JOINERS = {"，", "：", "、"}


def is_dash_run(text: str) -> bool:
    """True when a run is a standalone 破折號 (only dash chars, nothing else)."""
    return bool(text) and set(text) <= DASH_CHARS


# (unique paragraph anchor, [replacement per dash run in document order]).
# 「：」 introduces an enumeration that the 破折號 used to open, 「，」 joins a
# clause / appositive that the 破折號 used to break. Counts are asserted below.
RULES: list[tuple[str, list[str]]] = [
    ("加人工評分交叉驗證", ["，"]),
    ("而無需每次重新訓練模型", ["，"]),
    ("掛載多組任務適配器並動態切換", ["，"]),
    ("而非死記答案", ["，"]),
    ("多組可選之審查能力模組", ["：", "，"]),
    ("由 create_backend 工廠依設定建立具體後端", ["：", "，"]),
    ("作為 Student Base Model", ["，", "，"]),
    ("不如像人類資深審查者一樣分階段來看", ["，"]),
    ("亦不致遺失先前步驟之產出", ["，"]),
    ("是 Chain-of-Thought 在本框架中最直接之體現", ["，"]),
    ("動態追加一條「條件式第八條」", ["，"]),
    ("GitHub 之 PR Review API", ["，", "，"]),
    ("兩語料為一階訊號", ["，", "，"]),
    ("不自動寫入規則檔", ["，"]),
    ("常見之失敗模式為虛構符號名稱", ["，"]),
    ("僅於審查最末整批落盤", ["，"]),
    ("僅 log 並吞掉", ["，"]),
    ("註冊於 prthinker.review_modes", ["，"]),
    ("測試題目本身不能偏心", ["，"]),
    ("而是穩健可信的", ["，"]),
    ("是「整合框架內部之貢獻分解」", ["，"]),
    ("RQ1 得到正面回答", ["，"]),
    ("更進一步聚焦於 LLM 直接審查時浮現之三大問題", ["：", "，"]),
    ("此項工作之第一步", ["，", "，", "，"]),
]

EN_ANCHOR = "solves a different problem"  # English abstract: em-dashes in-run

paras = list(doc.paragraphs)
total = 0

for anchor, repls in RULES:
    hits = [p for p in paras if anchor in p.text]
    if len(hits) != 1:
        sys.exit(f"ABORT: anchor {anchor!r} matched {len(hits)} paragraphs (want 1)")
    p = hits[0]
    runs = p.runs
    dash_idx = [i for i, r in enumerate(runs) if is_dash_run(r.text)]
    if len(dash_idx) != len(repls):
        sys.exit(f"ABORT: {anchor!r} has {len(dash_idx)} dash runs, "
                 f"{len(repls)} replacements supplied")
    for i, repl in zip(dash_idx, repls):
        runs[i].text = repl
        total += 1
        if repl in CLAUSE_JOINERS:
            # full-width joiner needs no surrounding ASCII space
            if i > 0 and runs[i - 1].text.endswith(" "):
                runs[i - 1].text = runs[i - 1].text[:-1]
            if i + 1 < len(runs) and runs[i + 1].text.startswith(" "):
                runs[i + 1].text = runs[i + 1].text[1:]

def en_dedash(text: str) -> str:
    """English break-dash → comma. Drop the surrounding spaces a spaced dash
    carried (「code — only」→「code, only」) and the bare form too
    (「problem—preserving」→「problem, preserving」)."""
    for d in DASH_CHARS:
        text = text.replace(f" {d} ", ", ").replace(d, ", ")
    return text


# English abstract: em-dashes live inside a longer run.
en_hits = [p for p in paras if EN_ANCHOR in p.text]
if len(en_hits) != 1:
    sys.exit(f"ABORT: English anchor matched {len(en_hits)} paragraphs (want 1)")
for r in en_hits[0].runs:
    if any(c in DASH_CHARS for c in r.text) and not is_dash_run(r.text):
        r.text = en_dedash(r.text)
        total += 1

# Final sweep over EVERY <w:t> (body, tables, and figure/textbox drawings —
# the figure instruction line is stored twice, DrawingML Choice + VML Fallback,
# both fixed so they stay identical). A standalone CJK 破折號 here would mean a
# body anchor was missed → abort; an English break-dash is comma-fixed in place.
W_T = "}t"
for t in doc.element.iter():
    if not (t.tag.endswith(W_T) and t.text):
        continue
    if not any(c in DASH_CHARS for c in t.text):
        continue
    if any("a" <= c.lower() <= "z" for c in t.text):  # English context
        t.text = en_dedash(t.text)
        total += 1
    else:
        sys.exit(f"ABORT: un-anchored CJK 破折號 survived: {t.text!r}")

# Safety net: no em/box/bar dash may survive anywhere.
remaining = [t.text for t in doc.element.iter()
             if t.tag.endswith(W_T) and t.text
             and any(c in DASH_CHARS for c in t.text)]
if remaining:
    print("REMAINING DASHES (not fixed):")
    for t in remaining:
        print("  ", t[:80])
    sys.exit("ABORT: dashes still present")

doc.save(dst)
print(f"{src} -> {dst}：破折號 → 全形標點，共處理 {total} 段 dash，"
      f"剩餘 em/box/bar dash 0 處")
