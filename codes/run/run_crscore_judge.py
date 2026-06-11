"""Send crscore_llm_judge.md prompts to the GPT judge and aggregate scores.

Replicates the external judging step of the qwen3 crscore++ evaluation
(judge model per datas/Compare/CRSCORE.md: GPT-5). For every
cot_*/crscore_llm_judge.md under RESULTS_ROOT, asks the judge, parses the
"### Final Scores:" tuple, writes crscore_score.md next to the prompt,
then aggregates all tuples into all_crscore_score.md and a normalized
score.md (mean/5, matching the historical "normalize 0~1,1=0.2" table).

Requires OPENAI_API_KEY. Resumable: existing crscore_score.md is kept.

    PYTHONPATH=. python codes/run/run_crscore_judge.py \
        datas/Results/2026-06-11-gemma4-31b
"""

import os
import re
import sys
import time
from pathlib import Path

import httpx

JUDGE_MODEL = os.environ.get("JUDGE_MODEL", "gpt-5")
OPENAI_BASE = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
_SCORE_RE = re.compile(
    r'\(\s*"comprehensiveness"\s*:\s*(\d)\s*,\s*"conciseness"\s*:\s*(\d)\s*,'
    r'\s*"relevance"\s*:\s*(\d)\s*\)'
)
_MAX_ATTEMPTS = 3
_DIMENSIONS = ("comprehensiveness", "conciseness", "relevance")
_SCALE_MAX = 5


def _ask_judge(client: httpx.Client, prompt: str) -> str:
    response = client.post(
        "/chat/completions",
        json={
            "model": JUDGE_MODEL,
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def _judge_case(client: httpx.Client, folder: Path) -> tuple[int, int, int]:
    score_path = folder / "crscore_score.md"
    if score_path.exists():
        match = _SCORE_RE.search(score_path.read_text(encoding="utf-8"))
        if match:
            return tuple(int(g) for g in match.groups())
    prompt = (folder / "crscore_llm_judge.md").read_text(encoding="utf-8")
    last_error: Exception | None = None
    for attempt in range(1, _MAX_ATTEMPTS + 1):
        try:
            answer = _ask_judge(client, prompt)
            match = _SCORE_RE.search(answer)
            if match is None:
                raise ValueError("no Final Scores tuple in judge answer")
            scores = tuple(int(g) for g in match.groups())
            score_path.write_text(
                f'("comprehensiveness": {scores[0]}, "conciseness": '
                f'{scores[1]}, "relevance": {scores[2]})',
                encoding="utf-8",
            )
            (folder / "crscore_judge_answer.md").write_text(
                answer, encoding="utf-8"
            )
            return scores
        except (httpx.HTTPError, ValueError) as err:
            last_error = err
            print(f"{folder.name}: attempt {attempt} failed: {err}", flush=True)
            time.sleep(5 * attempt)
    raise RuntimeError(f"judge failed for {folder.name}") from last_error


def main(results_root: Path) -> None:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is not set")
    folders = sorted(
        p.parent for p in results_root.rglob("crscore_llm_judge.md")
    )
    if not folders:
        raise SystemExit(f"no crscore_llm_judge.md under {results_root}")
    all_scores: list[tuple[int, int, int]] = []
    with httpx.Client(
        base_url=OPENAI_BASE,
        timeout=300.0,
        headers={"Authorization": f"Bearer {api_key}"},
    ) as client:
        for folder in folders:
            scores = _judge_case(client, folder)
            print(folder.name, scores, flush=True)
            all_scores.append(scores)

    lines = [
        f'("comprehensiveness": {c}, "conciseness": {n}, "relevance": {r})'
        for c, n, r in all_scores
    ]
    (results_root / "all_crscore_score.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )

    means = [
        sum(s[i] for s in all_scores) / len(all_scores)
        for i in range(len(_DIMENSIONS))
    ]
    rows_01 = "\n".join(
        f"| {dim} | {mean / _SCALE_MAX:.2f} |"
        for dim, mean in zip(_DIMENSIONS, means)
    )
    rows_100 = "\n".join(
        f"| {dim} | {round(mean / _SCALE_MAX * 100)} |"
        for dim, mean in zip(_DIMENSIONS, means)
    )
    (results_root / "score.md").write_text(
        f"Judge: {JUDGE_MODEL} · {len(all_scores)} cases\n\n"
        f"| normalize 0~1,1=0.2 | gemma4-31b |\n|:---:|:---:|\n{rows_01}\n\n"
        f"| normalize 0~100,1=20 | gemma4-31b |\n|:---:|:---:|\n{rows_100}\n",
        encoding="utf-8",
    )
    print("score.md written to", results_root, flush=True)


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else
              "datas/Results/2026-06-11-gemma4-31b"))
