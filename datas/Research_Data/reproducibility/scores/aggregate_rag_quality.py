"""Aggregate paired five-dimension scores for the calibrated RAG experiment."""

from __future__ import annotations

import argparse
import json
import re
import statistics
from pathlib import Path

from scipy.stats import wilcoxon


DIMENSIONS = (
    "readability",
    "constructiveness",
    "correctness",
    "coverage",
    "comprehensiveness",
)
SCORE_RE = re.compile(r'"(' + "|".join(DIMENSIONS) + r')"\s*:\s*(\d+)')


def load_scores(root: Path) -> dict[str, dict[str, int]]:
    rows: dict[str, dict[str, int]] = {}
    for score_path in sorted(root.rglob("our_score_gpt56sol_rag.md")):
        case_id = score_path.parent.name
        values = {key: int(value) for key, value in SCORE_RE.findall(score_path.read_text(encoding="utf-8"))}
        if set(values) != set(DIMENSIONS):
            raise ValueError(f"incomplete score file: {score_path}")
        if case_id in rows:
            raise ValueError(f"duplicate case id: {case_id}")
        rows[case_id] = values
    return rows


def holm_adjust(p_values: dict[str, float]) -> dict[str, float]:
    ordered = sorted(p_values, key=p_values.get)
    adjusted: dict[str, float] = {}
    running = 0.0
    count = len(ordered)
    for rank, name in enumerate(ordered):
        candidate = min(1.0, (count - rank) * p_values[name])
        running = max(running, candidate)
        adjusted[name] = running
    return adjusted


def summarize(on: dict[str, dict[str, int]], off: dict[str, dict[str, int]]) -> dict:
    on_ids, off_ids = set(on), set(off)
    if on_ids != off_ids:
        raise ValueError(f"case mismatch: on_only={sorted(on_ids - off_ids)}, off_only={sorted(off_ids - on_ids)}")
    case_ids = sorted(on_ids)
    if not case_ids:
        raise ValueError("no paired cases")

    results: dict[str, dict] = {}
    raw_p: dict[str, float] = {}
    for dimension in DIMENSIONS:
        on_values = [on[case_id][dimension] for case_id in case_ids]
        off_values = [off[case_id][dimension] for case_id in case_ids]
        differences = [a - b for a, b in zip(on_values, off_values)]
        test = wilcoxon(on_values, off_values, alternative="two-sided", zero_method="wilcox", method="auto")
        p_value = float(test.pvalue)
        raw_p[dimension] = p_value
        results[dimension] = {
            "rag_on_mean": statistics.fmean(on_values),
            "rag_on_sample_sd": statistics.stdev(on_values),
            "rag_off_mean": statistics.fmean(off_values),
            "rag_off_sample_sd": statistics.stdev(off_values),
            "paired_mean_difference": statistics.fmean(differences),
            "paired_median_difference": statistics.median(differences),
            "wins": sum(value > 0 for value in differences),
            "ties": sum(value == 0 for value in differences),
            "losses": sum(value < 0 for value in differences),
            "wilcoxon_statistic": float(test.statistic),
            "wilcoxon_p_two_sided": p_value,
        }

    adjusted = holm_adjust(raw_p)
    for dimension in DIMENSIONS:
        results[dimension]["holm_adjusted_p"] = adjusted[dimension]
    return {
        "design": "paired",
        "n_pairs": len(case_ids),
        "judge": "gpt-5.6-sol",
        "score_range": [1, 100],
        "multiple_testing_correction": "Holm, family size 5",
        "dimensions": results,
        "case_ids": case_ids,
    }


def render_markdown(summary: dict) -> str:
    lines = [
        "# RAG 開關組五維度成對比較",
        "",
        f"配對案例數：{summary['n_pairs']}。評分者：{summary['judge']}。各維度範圍為 1 至 100 分。",
        "統計檢定採雙尾 Wilcoxon 符號等級檢定，並以 Holm 法校正五次檢定。",
        "",
        "| 維度 | RAG 開啟（平均±樣本標準差） | RAG 關閉（平均±樣本標準差） | 成對平均差 | 勝／同／負 | W | 未校正 p | Holm 校正 p |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    labels = {
        "readability": "可讀性",
        "constructiveness": "建設性",
        "correctness": "正確性",
        "coverage": "涵蓋度",
        "comprehensiveness": "完整性",
    }
    for dimension in DIMENSIONS:
        row = summary["dimensions"][dimension]
        lines.append(
            f"| {labels[dimension]} | {row['rag_on_mean']:.2f}±{row['rag_on_sample_sd']:.2f} | "
            f"{row['rag_off_mean']:.2f}±{row['rag_off_sample_sd']:.2f} | "
            f"{row['paired_mean_difference']:+.2f} | {row['wins']}／{row['ties']}／{row['losses']} | "
            f"{row['wilcoxon_statistic']:.1f} | {row['wilcoxon_p_two_sided']:.6g} | "
            f"{row['holm_adjusted_p']:.6g} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("experiment_root", type=Path)
    args = parser.parse_args()
    root = args.experiment_root
    summary = summarize(load_scores(root / "multi_rag_on"), load_scores(root / "multi_rag_off"))
    json_path = root / "rag_on_off_quality_summary.json"
    md_path = root / "rag_on_off_quality_summary.md"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(summary), encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()

