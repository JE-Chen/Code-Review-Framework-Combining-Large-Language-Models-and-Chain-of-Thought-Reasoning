"""Score issue coverage and precision for a generated review with Claude.

The output schema matches the 2026-07-19 objective experiment:
``coverage.json`` contains covered reference IDs and ``precision.json``
contains deduplicated issue-claim counts.  The batch is resumable.

Environment:
  EXP_ROOT       experiment directory to score
  GT_ROOT        directory containing the frozen reference JSON files
  CONDITIONS     comma-separated conditions, default multi_rag_on
  CASES_LIMIT    zero means all cases
  CLAUDE_MODEL   default opus
  CLAUDE_EFFORT  default high
"""
import json
import os
import shutil
import subprocess  # nosec B404 - fixed local CLI, argument list, no shell
import time
from pathlib import Path


REPO = Path(__file__).resolve().parents[4]
EXP = Path(os.environ.get(
    "EXP_ROOT", REPO / "datas" / "Results" / "2026-07-20-gemma4-rag-calibrated"
))
GT_ROOT = Path(os.environ.get(
    "GT_ROOT", REPO / "datas" / "Results" / "2026-07-19-gemma4-experiment" / "ground_truth"
))
DATA_ROOT = REPO / "datas" / "code_to_detect"
LOG = EXP / "objective_issue_judge.log"
MODEL = os.environ.get("CLAUDE_MODEL", "opus")
EFFORT = os.environ.get("CLAUDE_EFFORT", "high")
CLAUDE = shutil.which("claude") or "claude"

MULTI_FILES = (
    "first_summary_result.md",
    "first_code_review_result.md",
    "linter_result.md",
    "code_smell_result.md",
    "total_summary_result.md",
)
DATASETS = (
    ("bad_data/Python/ChatGPT", "cot_chatgpt_bad_data"),
    ("bad_data/Python/Copilot", "cot_copilot_bad_data"),
    ("code_diff/Python/ChatGPT", "cot_chatgpt_code_diff"),
    ("code_diff/Python/Copilot", "cot_copilot_code_diff"),
    ("only_code/Python/ChatGPT", "cot_chatgpt_only_code"),
    ("only_code/Python/Copilot", "cot_copilot_only_code"),
)

INSTRUCTIONS = """You are an independent code-review evaluator. Compare the
source code, frozen reference issue list, and review output below.

Coverage rules:
- Return a reference ID only when the review clearly identifies the same
  underlying issue. Equivalent wording is acceptable; a vague generic warning
  is not.
- Use only IDs present in REFERENCE ISSUES.

Precision rules:
- Count unique substantive problem claims in the entire review. Deduplicate
  repetitions across stages and do not count strengths, headings, or a repair
  suggestion without a claimed problem.
- Validate every claim directly against SOURCE CODE. The reference list may be
  incomplete, so a real claim can be valid even when it has no reference ID.
- Put each unsupported or materially incorrect claim in false_positives.
- claims must equal valid plus the number of false_positives.

Output ONLY one JSON object:
{"covered_ids":["exact-id"],"total":N,"claims":N,"valid":N,
 "false_positives":["brief unsupported claim"]}
"""


def log(*parts):
    line = f"{time.strftime('%H:%M:%S')} " + " ".join(str(p) for p in parts)
    print(line, flush=True)
    EXP.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def cases():
    out = []
    for sub, prefix in DATASETS:
        folder = DATA_ROOT / sub.replace("/", os.sep)
        for source_path in sorted(folder.iterdir()):
            if source_path.is_file():
                out.append((f"{prefix}_{source_path.stem}", source_path))
    return out


def review_text(condition, case):
    case_dir = EXP / condition / "cot" / case
    if condition.startswith("multi_"):
        parts = []
        for name in MULTI_FILES:
            path = case_dir / name
            if path.exists():
                parts.append(f"## {name}\n{path.read_text(encoding='utf-8', errors='replace')}")
        return "\n\n".join(parts)
    path = case_dir / "single_code_review_prompt_result.md"
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def extract_object(text):
    start = text.find("{")
    while start != -1:
        try:
            value, _ = json.JSONDecoder().raw_decode(text[start:])
            if isinstance(value, dict) and "covered_ids" in value:
                return value
        except json.JSONDecodeError:
            pass
        start = text.find("{", start + 1)
    raise ValueError("no result JSON object in Claude output")


def judge(source, reference, review):
    prompt = (
        INSTRUCTIONS
        + "\n\nSOURCE CODE\n```\n" + source + "\n```"
        + "\n\nREFERENCE ISSUES\n" + json.dumps(reference, ensure_ascii=False, indent=2)
        + "\n\nREVIEW OUTPUT\n" + review
    )
    proc = subprocess.run(  # nosec B603 - fixed executable and argument list
        [CLAUDE, "-p", "--model", MODEL, "--effort", EFFORT,
         "--output-format", "text", "--no-session-persistence",
         "--disable-slash-commands", "--tools", ""],
        input=prompt,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=600,
        cwd=str(REPO),
    )
    raw = (proc.stdout or "") + "\n" + (proc.stderr or "")
    if proc.returncode:
        raise RuntimeError(f"Claude exit {proc.returncode}: {raw[-1000:]}")
    return extract_object(raw), raw


def validate(result, reference):
    valid_ids = {item["id"] for item in reference}
    covered = result.get("covered_ids")
    false_positives = result.get("false_positives")
    if not isinstance(covered, list) or not set(covered) <= valid_ids:
        raise ValueError("covered_ids contains an unknown ID")
    if not isinstance(false_positives, list):
        raise ValueError("false_positives is not a list")
    claims = int(result["claims"])
    valid = int(result["valid"])
    if claims != valid + len(false_positives):
        raise ValueError("claims != valid + false positives")
    return {
        "covered_ids": covered,
        "total": len(reference),
        "claims": claims,
        "valid": valid,
        "false_positives": false_positives,
    }


def main():
    selected = cases()
    limit = int(os.environ.get("CASES_LIMIT", "0"))
    if limit:
        selected = selected[:limit]
    conditions = [x.strip() for x in os.environ.get(
        "CONDITIONS", "multi_rag_on"
    ).split(",") if x.strip()]
    log(f"START model={MODEL} cases={len(selected)} conditions={conditions}")
    for condition in conditions:
        for index, (case, source_path) in enumerate(selected, 1):
            case_dir = EXP / condition / "cot" / case
            coverage_path = case_dir / "coverage.json"
            precision_path = case_dir / "precision.json"
            if coverage_path.exists() and precision_path.exists():
                log(f"[{condition} {index}/{len(selected)}] {case} skip")
                continue
            try:
                review = review_text(condition, case)
                if not review.strip():
                    log(f"[{condition} {index}/{len(selected)}] {case} EMPTY skip")
                    continue
                reference = json.loads((GT_ROOT / f"{case}.json").read_text(encoding="utf-8"))
                source = source_path.read_text(encoding="utf-8", errors="replace")
                started = time.time()
                result, raw = judge(source, reference, review)
                result = validate(result, reference)
                case_dir.mkdir(parents=True, exist_ok=True)
                coverage_path.write_text(json.dumps({
                    "covered_ids": result["covered_ids"], "total": result["total"]
                }, ensure_ascii=False, indent=2), encoding="utf-8")
                precision_path.write_text(json.dumps({
                    "claims": result["claims"], "valid": result["valid"],
                    "false_positives": result["false_positives"]
                }, ensure_ascii=False, indent=2), encoding="utf-8")
                log(f"[{condition} {index}/{len(selected)}] {case} done "
                    f"{int(time.time()-started)}s covered={len(result['covered_ids'])} "
                    f"valid={result['valid']}/{result['claims']}")
            except Exception as exc:  # noqa: BLE001 - preserve resumable batch
                case_dir.mkdir(parents=True, exist_ok=True)
                (case_dir / "objective_judge_error.txt").write_text(
                    repr(exc) + "\n", encoding="utf-8"
                )
                log(f"[{condition} {index}/{len(selected)}] {case} ERROR {exc!r}")
    log("ALL DONE")


if __name__ == "__main__":
    main()
