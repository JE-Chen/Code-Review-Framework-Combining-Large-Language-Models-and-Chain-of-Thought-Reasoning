"""Drive the live Gemma server (pr-thinker-2.sdpmlab.org) to regenerate the
ablation data: multi-stage (RAG on / RAG off) via /review, single-prompt via
/ask. Resumable — skips cases whose primary output already exists. Writes each
result to disk immediately so a restart resumes where it left off.

Env:
  CASES_LIMIT   process only the first N cases per condition (0 = all)
  CONDITIONS    comma list subset of: multi_rag_on,single,multi_rag_off
  OUT_ROOT      new run directory; do not reuse a completed experiment
  RAG_THRESHOLD embedding-model-calibrated cutoff (default 0.32)
  PRTHINKER_BASE_URL server base URL
  EXPECTED_RAG_MODE / EXPECTED_RAG_CORPUS / EXPECTED_LORA_ENABLED
                  optional preflight assertions against /healthz
"""
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = os.environ.get(
    "PRTHINKER_BASE_URL", "https://pr-thinker-2.sdpmlab.org"
).rstrip("/")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
REPO = Path(r"D:\Codes\Code-Review-Framework-Combining-Large-Language-Models-and-Chain-of-Thought-Reasoning")
DATA_ROOT = REPO / "datas" / "code_to_detect"
OUT_ROOT = Path(os.environ.get(
    "OUT_ROOT", REPO / "datas" / "Results" / "2026-07-20-gemma4-rag-calibrated"
))
RAG_THRESHOLD = float(os.environ.get("RAG_THRESHOLD", "0.32"))
LOG = OUT_ROOT / "run.log"
SERVER_MANIFEST = OUT_ROOT / "server_manifest.json"

SINGLE_CODE_REVIEW_PROMPT = (
    "\nYou are an experienced software engineer and code reviewer. \n"
    "Your task is to carefully review the following code and provide constructive feedback.\n\n"
    "### Goals of the review:\n1. **Best Practices**\n2. **Linter Messages**\n3. **Code Smells**\n\n"
    "### Instructions:\n- Provide specific examples of issues and explain why they matter.\n"
    "- Suggest concrete improvements (e.g., refactoring, better variable names, modularization).\n"
    "- Highlight both strengths and weaknesses of the code.\n"
    "- Keep feedback concise, actionable, and professional.\n"
    "- Organize feedback by category (Linter, Code Smell, etc.).\n\n"
    "### Code to review:\n{code_diff}\n"
)

DATASETS = (
    ("bad_data/Python/ChatGPT", "cot_chatgpt_bad_data"),
    ("bad_data/Python/Copilot", "cot_copilot_bad_data"),
    ("code_diff/Python/ChatGPT", "cot_chatgpt_code_diff"),
    ("code_diff/Python/Copilot", "cot_copilot_code_diff"),
    ("only_code/Python/ChatGPT", "cot_chatgpt_only_code"),
    ("only_code/Python/Copilot", "cot_copilot_only_code"),
)
STEP_FILE = {
    "first_summary": "first_summary_result.md",
    "first_code_review": "first_code_review_result.md",
    "linter": "linter_result.md",
    "code_smell": "code_smell_result.md",
    "total_summary": "total_summary_result.md",
}
POLL_SECS = 20
JOB_MAX_SECS = 1500  # 25 min per job ceiling


def log(*parts):
    msg = " ".join(str(p) for p in parts)
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    print(line, flush=True)
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def _req(path, payload=None):
    url = BASE + path
    headers = {"User-Agent": UA}
    data = None
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, data=data, headers=headers,
                                         method="POST" if payload is not None else "GET")
            with urllib.request.urlopen(req, timeout=90) as resp:  # nosec B310 - https literal base
                return json.loads(resp.read())
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            if attempt == 3:
                raise
            time.sleep(5 * (attempt + 1))
            log("  retry", path, repr(exc))
    return None


def _run_job(submit_path, result_path_tmpl, payload):
    sub = _req(submit_path, payload)
    jid = sub["job_id"]
    t0 = time.time()
    while time.time() - t0 < JOB_MAX_SECS:
        st = _req(result_path_tmpl.format(jid=jid))
        if st["status"] == "done":
            return st["result"], int(time.time() - t0)
        if st["status"] in ("error", "cancelled"):
            raise RuntimeError(f"job {jid} {st['status']}: {st.get('error')}")
        time.sleep(POLL_SECS)
    raise TimeoutError(f"job {jid} exceeded {JOB_MAX_SECS}s")


def _server_preflight():
    health = _req("/healthz")
    expected = {
        "rag_mode": os.environ.get("EXPECTED_RAG_MODE"),
        "rag_corpus": os.environ.get("EXPECTED_RAG_CORPUS"),
    }
    if os.environ.get("EXPECTED_LORA_ENABLED") is not None:
        expected["lora_enabled"] = (
            os.environ["EXPECTED_LORA_ENABLED"].strip().lower()
            in {"1", "true", "yes"}
        )
    mismatches = {
        key: {"expected": value, "actual": health.get(key)}
        for key, value in expected.items()
        if value is not None and health.get(key) != value
    }
    if mismatches:
        raise RuntimeError(f"server experiment configuration mismatch: {mismatches}")
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    SERVER_MANIFEST.write_text(
        json.dumps(health, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return health


def _cases():
    out = []
    for sub, prefix in DATASETS:
        d = DATA_ROOT / sub.replace("/", os.sep)
        for fp in sorted(d.iterdir()):
            if fp.is_file():
                out.append((f"{prefix}_{fp.stem}", fp.read_text(encoding="utf-8", errors="replace")))
    return out


def do_multi(case, src, rag_on):
    cond = "multi_rag_on" if rag_on else "multi_rag_off"
    cdir = OUT_ROOT / cond / "cot" / case
    if (cdir / "total_summary_result.md").exists():
        return "skip"
    cdir.mkdir(parents=True, exist_ok=True)
    result, secs = _run_job(
        "/review/submit", "/review/result/{jid}",
        {"code_diff": src, "file_path": f"{case}.py", "rag_enabled": rag_on,
         "rag_threshold": RAG_THRESHOLD, "max_new_tokens": 8192, "step_plan": "full"},
    )
    for step in result.get("steps", []):
        fname = STEP_FILE.get(step["name"])
        if fname:
            (cdir / fname).write_text(step["output"], encoding="utf-8")
    (cdir / "rag_docs.json").write_text(json.dumps(result.get("rag_docs", [])), encoding="utf-8")
    (cdir / "inline_findings.json").write_text(
        json.dumps(result.get("inline_findings", [])), encoding="utf-8")
    return f"done {secs}s rag_docs={len(result.get('rag_docs', []))}"


def do_single(case, src):
    cdir = OUT_ROOT / "single" / "cot" / case
    if (cdir / "single_code_review_prompt_result.md").exists():
        return "skip"
    cdir.mkdir(parents=True, exist_ok=True)
    result, secs = _run_job(
        "/ask/submit", "/ask/result/{jid}",
        {"prompt": SINGLE_CODE_REVIEW_PROMPT.format(code_diff=src), "max_new_tokens": 8192},
    )
    (cdir / "single_code_review_prompt_result.md").write_text(result, encoding="utf-8")
    return f"done {secs}s"


def main():
    limit = int(os.environ.get("CASES_LIMIT", "0"))
    conds = os.environ.get("CONDITIONS", "multi_rag_on,single,multi_rag_off").split(",")
    cases = _cases()
    if limit:
        cases = cases[:limit]
    health = _server_preflight()
    log(f"START {len(cases)} cases, conditions={conds}, server={health}")
    # Conditions-outer so the primary multi_rag_on data finishes first.
    for cond in conds:
        for i, (case, src) in enumerate(cases, 1):
            try:
                if cond == "multi_rag_on":
                    res = do_multi(case, src, True)
                elif cond == "multi_rag_off":
                    res = do_multi(case, src, False)
                elif cond == "single":
                    res = do_single(case, src)
                else:
                    res = f"unknown cond {cond}"
                log(f"[{cond} {i}/{len(cases)}] {case} ->", res)
            except Exception as exc:  # noqa: BLE001 - keep the batch alive; log and continue
                log(f"[{cond} {i}/{len(cases)}] {case} ERROR", repr(exc))
    log("ALL DONE")


if __name__ == "__main__":
    main()
