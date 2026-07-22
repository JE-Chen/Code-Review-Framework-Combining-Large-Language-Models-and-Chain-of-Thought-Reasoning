"""Phase A of the objective bug-detection experiment: build a ground-truth
issue list per case with gpt-5.6-sol looking ONLY at the source code (no
review). Independent of both pipelines. Resumable.
"""
import json
import os
import re
import shutil
import subprocess  # nosec B404 - local codex CLI, arg list, no shell
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
DATA_ROOT = REPO / "datas" / "code_to_detect"
OUT = REPO / "datas" / "Results" / "2026-07-19-gemma4-experiment" / "ground_truth"
LOG = OUT / "gt.log"
MODEL = os.environ.get("CODEX_MODEL", "gpt-5.6-sol")
EFFORT = os.environ.get("CODEX_EFFORT", "medium")
CODEX = shutil.which("codex") or "codex"

PROMPT = (
    "You are a senior code reviewer. Analyze ONLY the code provided via stdin. "
    "List every real, verifiable issue: bugs, security vulnerabilities, correctness "
    "errors, and significant maintainability/design problems or code smells. Exclude "
    "trivial style nits. Output ONLY a JSON array and nothing else, each element: "
    '{"id":"short-kebab-id","desc":"one-line description",'
    '"category":"bug|security|correctness|maintainability|smell",'
    '"severity":"critical|high|medium|low"}'
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
    OUT.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def _cases():
    out = []
    for sub, prefix in DATASETS:
        d = DATA_ROOT / sub.replace("/", os.sep)
        for fp in sorted(d.iterdir()):
            if fp.is_file():
                out.append((f"{prefix}_{fp.stem}", fp))
    return out


def _extract_json_array(text):
    start = text.find("[")
    while start != -1:
        try:
            arr, _ = json.JSONDecoder().raw_decode(text[start:])
            if isinstance(arr, list):
                return arr
        except json.JSONDecodeError:
            pass
        start = text.find("[", start + 1)
    raise ValueError("no JSON array in output")


def _enumerate(src):
    proc = subprocess.run(  # nosec B603 - fixed codex exe, arg list, no shell
        [CODEX, "exec", "-m", MODEL, "-c", f"model_reasoning_effort={EFFORT}",
         "-s", "read-only", "--skip-git-repo-check", PROMPT],
        input=src, capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=420, cwd=str(REPO),
    )
    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    return _extract_json_array(out)


def main():
    cases = _cases()
    limit = int(os.environ.get("CASES_LIMIT", "0"))
    if limit:
        cases = cases[:limit]
    log(f"START ground-truth model={MODEL} cases={len(cases)}")
    for i, (case, src_path) in enumerate(cases, 1):
        out = OUT / f"{case}.json"
        if out.exists():
            log(f"[{i}/{len(cases)}] {case} skip")
            continue
        try:
            src = src_path.read_text(encoding="utf-8", errors="replace")
            t0 = time.time()
            issues = _enumerate(src)
            out.write_text(json.dumps(issues, ensure_ascii=False, indent=2), encoding="utf-8")
            log(f"[{i}/{len(cases)}] {case} done {int(time.time()-t0)}s issues={len(issues)}")
        except Exception as exc:  # noqa: BLE001 - keep batch alive
            log(f"[{i}/{len(cases)}] {case} ERROR {exc!r}")
    log("ALL DONE")


if __name__ == "__main__":
    main()
