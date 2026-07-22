"""Score RAG-on and RAG-off multi-stage reviews with the Codex judge.

The batch is resumable and writes one score file per case.  It intentionally
scores only the final consolidated review for an apples-to-apples comparison.
"""
import os
import re
import shutil
import subprocess  # nosec B404 - fixed executable and argument list
import time
from pathlib import Path


REPO = Path(__file__).resolve().parents[4]
EXP = Path(os.environ.get(
    "EXP_ROOT", REPO / "datas" / "Results" / "2026-07-20-gemma4-rag-calibrated"
))
DATA_ROOT = REPO / "datas" / "code_to_detect"
LOG = EXP / "codex_judge_rag.log"
MODEL = os.environ.get("CODEX_MODEL", "gpt-5.6-sol")
EFFORT = os.environ.get("CODEX_EFFORT", "medium")
SCORE_FILE = os.environ.get("SCORE_FILE", "our_score_gpt56sol_rag.md")
CODEX = shutil.which("codex") or "codex"

PROMPT = (
    "Act as an LLM-as-a-Judge. The code-review text to evaluate is provided via stdin. "
    "Score it on five dimensions, integers 1-100: readability, constructiveness "
    "(maintainability/actionability), correctness, coverage (multi-review coverage and "
    "self-contained extractability of each finding), comprehensiveness (covers important "
    "issues including linter and code-smell findings). Judge only the review text given. "
    "Output ONLY this one line: "
    '("readability": N, "constructiveness": N, "correctness": N, '
    '"coverage": N, "comprehensiveness": N)'
)
SCORE_RE = re.compile(
    r'\(\s*"readability":\s*(\d+),\s*"constructiveness":\s*(\d+),'
    r'\s*"correctness":\s*(\d+),\s*"coverage":\s*(\d+),'
    r'\s*"comprehensiveness":\s*(\d+)\s*\)'
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
    with open(LOG, "a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def cases():
    result = []
    for subdir, prefix in DATASETS:
        folder = DATA_ROOT / subdir.replace("/", os.sep)
        result.extend(f"{prefix}_{path.stem}" for path in sorted(folder.iterdir()) if path.is_file())
    return result


def judge(review):
    proc = subprocess.run(  # nosec B603
        [CODEX, "exec", "-m", MODEL, "-c", f"model_reasoning_effort={EFFORT}",
         "-s", "read-only", "--skip-git-repo-check", PROMPT],
        input=review,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=360,
        cwd=str(REPO),
    )
    output = (proc.stdout or "") + "\n" + (proc.stderr or "")
    matches = SCORE_RE.findall(output)
    if proc.returncode or not matches:
        raise RuntimeError(f"Codex scoring failed ({proc.returncode}): {output[-1000:]}")
    readability, constructiveness, correctness, coverage, comprehensiveness = matches[-1]
    return (
        f'("readability": {readability}, "constructiveness": {constructiveness}, '
        f'"correctness": {correctness}, "coverage": {coverage}, '
        f'"comprehensiveness": {comprehensiveness})'
    )


def main():
    selected = cases()
    limit = int(os.environ.get("CASES_LIMIT", "0"))
    if limit:
        selected = selected[:limit]
    conditions = [item.strip() for item in os.environ.get(
        "CONDITIONS", "multi_rag_on,multi_rag_off"
    ).split(",") if item.strip()]
    log(f"START model={MODEL} cases={len(selected)} conditions={conditions}")
    for condition in conditions:
        for index, case in enumerate(selected, 1):
            case_dir = EXP / condition / "cot" / case
            output_path = case_dir / SCORE_FILE
            if output_path.exists():
                log(f"[{condition} {index}/{len(selected)}] {case} skip")
                continue
            review_path = case_dir / "total_summary_result.md"
            if not review_path.exists():
                log(f"[{condition} {index}/{len(selected)}] {case} EMPTY skip")
                continue
            try:
                started = time.time()
                score = judge(review_path.read_text(encoding="utf-8", errors="replace"))
                output_path.write_text(score + "\n", encoding="utf-8")
                log(f"[{condition} {index}/{len(selected)}] {case} done "
                    f"{int(time.time()-started)}s {score}")
            except Exception as exc:  # noqa: BLE001 - resumable batch
                log(f"[{condition} {index}/{len(selected)}] {case} ERROR {exc!r}")
    log("ALL DONE")


if __name__ == "__main__":
    main()
