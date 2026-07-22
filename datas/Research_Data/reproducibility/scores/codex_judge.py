"""Second independent judge: score the fresh Gemma reviews with GPT-5 via the
local codex CLI (ChatGPT-account; gpt-5.4-mini). Cross-judge robustness check
against the Claude scores. Writes our_score_gpt5.md per case/condition.
Resumable: skips any case whose our_score_gpt5.md already exists.

Env: CASES_LIMIT (0=all), CONDITIONS (comma list of multi_rag_on,single),
EXP_ROOT (experiment directory).
"""
import os
import re
import shutil
import subprocess  # nosec B404 - invoking the local codex CLI with an arg list
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
EXP = Path(os.environ.get(
    "EXP_ROOT", REPO / "datas" / "Results" / "2026-07-19-gemma4-experiment"
))
DATA_ROOT = REPO / "datas" / "code_to_detect"
LOG = EXP / "codex_judge.log"
MODEL = os.environ.get("CODEX_MODEL", "gpt-5.6-sol")
EFFORT = os.environ.get("CODEX_EFFORT", "medium")
SCORE_FILE = os.environ.get("SCORE_FILE", "our_score_gpt56sol.md")
CODEX = shutil.which("codex") or "codex"

# The multi-stage "final review" a user consumes is the consolidated total_summary.
# first_summary/first_code_review are intermediate drafts that repeat the same
# findings; concatenating them triple-counts and wrongly tanks readability. Score
# the final consolidated output only, apples-to-apples with the single review.
MULTI_FILES = (
    "total_summary_result.md",
)
PROMPT = (
    "Act as an LLM-as-a-Judge. The code-review text to evaluate is provided via stdin. "
    "Score it on five dimensions, integers 1-100: readability, constructiveness "
    "(maintainability/actionability), correctness, coverage (multi-review coverage and "
    "self-contained extractability of each finding), comprehensiveness (covers the important "
    "issues including linter and code-smell findings). Judge only the review text given; the "
    "raw code diff is intentionally omitted. Output ONLY this one line, nothing else: "
    '("readability": N, "constructiveness": N, "correctness": N, "coverage": N, "comprehensiveness": N)'
)
SCORE_RE = re.compile(
    r'\(\s*"readability":\s*(\d+),\s*"constructiveness":\s*(\d+),\s*"correctness":\s*(\d+),'
    r'\s*"coverage":\s*(\d+),\s*"comprehensiveness":\s*(\d+)\s*\)'
)
DATASETS = (
    ("bad_data/Python/ChatGPT", "cot_chatgpt_bad_data"),
    ("bad_data/Python/Copilot", "cot_copilot_bad_data"),
    ("code_diff/Python/ChatGPT", "cot_chatgpt_code_diff"),
    ("code_diff/Python/Copilot", "cot_copilot_code_diff"),
    ("only_code/Python/ChatGPT", "cot_chatgpt_only_code"),
    ("only_code/Python/Copilot", "cot_copilot_only_code"),
)


def log(*parts):
    line = f"{time.strftime('%H:%M:%S')} " + " ".join(str(p) for p in parts)
    print(line, flush=True)
    EXP.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def _cases():
    out = []
    for sub, prefix in DATASETS:
        d = DATA_ROOT / sub.replace("/", os.sep)
        for fp in sorted(d.iterdir()):
            if fp.is_file():
                out.append(f"{prefix}_{fp.stem}")
    return out


def _review_text(cond, case):
    cdir = EXP / cond / "cot" / case
    if cond == "multi_rag_on":
        parts = []
        for name in MULTI_FILES:
            fp = cdir / name
            if fp.exists():
                parts.append(fp.read_text(encoding="utf-8", errors="replace"))
        return "\n\n".join(parts)
    fp = cdir / "single_code_review_prompt_result.md"
    return fp.read_text(encoding="utf-8", errors="replace") if fp.exists() else ""


def _judge(review):
    proc = subprocess.run(  # nosec B603 - fixed codex executable, arg list, no shell
        [CODEX, "exec", "-m", MODEL, "-c", f"model_reasoning_effort={EFFORT}",
         "-s", "read-only", "--skip-git-repo-check", PROMPT],
        input=review, capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=360, cwd=str(REPO),
    )
    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    matches = SCORE_RE.findall(out)
    if not matches:
        raise ValueError("no score line in codex output")
    r, c, co, cov, comp = matches[-1]
    return (f'("readability": {r}, "constructiveness": {c}, "correctness": {co}, '
            f'"coverage": {cov}, "comprehensiveness": {comp})')


def main():
    limit = int(os.environ.get("CASES_LIMIT", "0"))
    conds = os.environ.get("CONDITIONS", "multi_rag_on,single").split(",")
    cases = _cases()
    if limit:
        cases = cases[:limit]
    log(f"START codex judge model={MODEL} cases={len(cases)} conds={conds}")
    for cond in conds:
        for i, case in enumerate(cases, 1):
            out = EXP / cond / "cot" / case / SCORE_FILE
            if out.exists():
                log(f"[{cond} {i}/{len(cases)}] {case} skip")
                continue
            try:
                review = _review_text(cond, case)
                if not review.strip():
                    log(f"[{cond} {i}/{len(cases)}] {case} EMPTY-review skip")
                    continue
                t0 = time.time()
                score = _judge(review)
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(score + "\n", encoding="utf-8")
                log(f"[{cond} {i}/{len(cases)}] {case} done {int(time.time()-t0)}s {score}")
            except Exception as exc:  # noqa: BLE001 - keep batch alive; log and continue
                log(f"[{cond} {i}/{len(cases)}] {case} ERROR {exc!r}")
    log("ALL DONE")


if __name__ == "__main__":
    main()
