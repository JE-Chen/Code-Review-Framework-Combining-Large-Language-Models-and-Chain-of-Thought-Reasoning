"""Audit RAG retrieval hits for the 44-case thesis corpus.

This calls only the remote /rag endpoint.  It does not invoke the review
generator and never sends ground-truth annotations to the service.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import urllib.request
from collections import Counter
from pathlib import Path

BASE = os.environ.get("PRTHINKER_BASE_URL", "https://pr-thinker-2.sdpmlab.org").rstrip("/")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
REPO = Path(__file__).resolve().parents[1]
DATA_ROOT = REPO / "datas" / "code_to_detect"
OUT = REPO / "datas" / "Results" / "2026-07-20-rag-hit-audit.json"
THRESHOLDS = (0.70, 0.32)
DATASETS = (
    ("bad_data/Python/ChatGPT", "cot_chatgpt_bad_data"),
    ("bad_data/Python/Copilot", "cot_copilot_bad_data"),
    ("code_diff/Python/ChatGPT", "cot_chatgpt_code_diff"),
    ("code_diff/Python/Copilot", "cot_copilot_code_diff"),
    ("only_code/Python/ChatGPT", "cot_chatgpt_only_code"),
    ("only_code/Python/Copilot", "cot_copilot_only_code"),
)


def cases() -> list[tuple[str, str]]:
    rows = []
    for relative, prefix in DATASETS:
        for path in sorted((DATA_ROOT / relative).iterdir()):
            if path.is_file():
                rows.append((f"{prefix}_{path.stem}", path.read_text("utf-8", errors="replace")))
    return rows


def retrieve(query: str, threshold: float) -> list[str]:
    payload = json.dumps({"query": query, "threshold": threshold, "k": 15}).encode()
    req = urllib.request.Request(
        BASE + "/rag",
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": USER_AGENT},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as response:  # nosec B310 - configured HTTPS endpoint
        return json.loads(response.read())["docs"]



def main() -> None:
    source_cases = cases()
    runs = {}
    for threshold in THRESHOLDS:
        per_case = []
        for case_id, query in source_cases:
            docs = retrieve(query, threshold)
            per_case.append({
                "case_id": case_id,
                "retrieved_count": len(docs),
                "retrieved_sha256": [hashlib.sha256(d.encode()).hexdigest() for d in docs],
            })
            print(f"{threshold:.2f} {case_id}: {len(docs)}", flush=True)
        counts = [row["retrieved_count"] for row in per_case]
        runs[f"{threshold:.2f}"] = {
            "cases_with_hits": sum(value > 0 for value in counts),
            "total_cases": len(counts),
            "total_retrieved": sum(counts),
            "mean_retrieved_per_case": sum(counts) / len(counts),
            "count_distribution": dict(sorted(Counter(counts).items())),
            "per_case": per_case,
        }
    artifact = {
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "endpoint": BASE,
        "query_corpus": "datas/code_to_detect (44 files; ground truth excluded)",
        "runs": runs,
    }
    OUT.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: {k: v for k, v in value.items() if k != "per_case"} for key, value in runs.items()}, indent=2))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
