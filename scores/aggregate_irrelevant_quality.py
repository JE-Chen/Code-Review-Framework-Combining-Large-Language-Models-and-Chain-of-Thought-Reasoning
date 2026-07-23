"""Aggregate the fixed irrelevant-rule injection group against the RAG-off
baseline as a paired five-dimension comparison.

Reuses the calibrated RAG experiment's pairing logic (``load_scores``,
``summarize``, Holm correction) from :mod:`aggregate_rag_quality`, so the
statistics are byte-for-byte identical to the RAG on/off table; only the
condition labels differ. Condition A is ``multi_irrelevant_fixed`` (three fixed
irrelevant rules injected via ``extra_rules``); condition B is the identical
``multi_rag_off`` pipeline with no injection. The paired difference is reported
as ``A minus B``.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from aggregate_rag_quality import DIMENSIONS, load_scores, summarize

LABELS = {
    "readability": "可讀性",
    "constructiveness": "建設性",
    "correctness": "正確性",
    "coverage": "涵蓋度",
    "comprehensiveness": "完整性",
}
KEY_RENAME = {
    "rag_on_mean": "inject_mean",
    "rag_on_sample_sd": "inject_sample_sd",
    "rag_off_mean": "baseline_mean",
    "rag_off_sample_sd": "baseline_sample_sd",
}


def relabel(summary: dict) -> dict:
    """Rename the RAG-oriented keys to injection-vs-baseline keys in place."""
    for row in summary["dimensions"].values():
        for old, new in KEY_RENAME.items():
            row[new] = row.pop(old)
    summary["conditions"] = {
        "A_inject": "multi_irrelevant_fixed (three fixed irrelevant rules "
                    "injected via extra_rules)",
        "B_baseline": "multi_rag_off (identical rag-off pipeline, no injection)",
    }
    summary["difference_direction"] = "inject minus baseline"
    return summary


def render_markdown(summary: dict) -> str:
    """Render the paired comparison as a full-width-punctuation table."""
    lines = [
        "# 固定注入無關規則組與 RAG 關閉基準五維度成對比較",
        "",
        f"配對案例數：{summary['n_pairs']}。評分者：{summary['judge']}。"
        "各維度範圍為 1 至 100 分。",
        "統計檢定採雙尾 Wilcoxon 符號等級檢定，並以 Holm 法校正五次檢定。"
        "成對平均差方向為「注入無關規則減基準」。",
        "",
        "| 維度 | 注入無關規則（平均±樣本標準差） | "
        "RAG 關閉基準（平均±樣本標準差） | 成對平均差 | 勝／同／負 | W | "
        "未校正 p | Holm 校正 p |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for dimension in DIMENSIONS:
        row = summary["dimensions"][dimension]
        lines.append(
            f"| {LABELS[dimension]} | "
            f"{row['inject_mean']:.2f}±{row['inject_sample_sd']:.2f} | "
            f"{row['baseline_mean']:.2f}±{row['baseline_sample_sd']:.2f} | "
            f"{row['paired_mean_difference']:+.2f} | "
            f"{row['wins']}／{row['ties']}／{row['losses']} | "
            f"{row['wilcoxon_statistic']:.1f} | "
            f"{row['wilcoxon_p_two_sided']:.6g} | "
            f"{row['holm_adjusted_p']:.6g} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("inject_root", type=Path, help=".../multi_irrelevant_fixed")
    parser.add_argument("baseline_root", type=Path, help=".../multi_rag_off")
    parser.add_argument("--out", type=Path, required=True,
                        help="output directory for the summary files")
    args = parser.parse_args()
    summary = relabel(
        summarize(load_scores(args.inject_root), load_scores(args.baseline_root))
    )
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "irrelevant_vs_ragoff_quality_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    markdown = render_markdown(summary)
    (args.out / "irrelevant_vs_ragoff_quality_summary.md").write_text(
        markdown, encoding="utf-8"
    )
    print(markdown)


if __name__ == "__main__":
    main()
