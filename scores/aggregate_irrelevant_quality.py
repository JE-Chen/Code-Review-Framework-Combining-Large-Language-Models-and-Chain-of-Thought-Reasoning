"""Aggregate a direct-injection group against a rag-off baseline as a paired
five-dimension comparison.

Reuses the calibrated RAG experiment's pairing logic (``load_scores``,
``summarize``, Holm correction) from :mod:`aggregate_rag_quality`, so the
statistics are byte-for-byte identical to the RAG on/off table; only the
condition labels differ. Condition A is the injection group (three fixed
irrelevant rules, or the full relevant corpus, injected via ``extra_rules``);
condition B is the identical ``multi_rag_off`` pipeline with no injection. The
paired difference is reported as ``A minus B``.

Labels default to the fixed-irrelevant comparison and are overridable so the
same script serves the full-rule direct-injection group.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from aggregate_rag_quality import DIMENSIONS, SCORE_FILE, load_scores, summarize

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


def relabel(summary: dict, inject_desc: str, baseline_desc: str) -> dict:
    """Rename the RAG-oriented keys to injection-vs-baseline keys in place."""
    for row in summary["dimensions"].values():
        for old, new in KEY_RENAME.items():
            row[new] = row.pop(old)
    summary["conditions"] = {"A_inject": inject_desc, "B_baseline": baseline_desc}
    summary["difference_direction"] = "inject minus baseline"
    return summary


def render_markdown(summary: dict, title: str, inject_label: str,
                    baseline_label: str) -> str:
    """Render the paired comparison as a full-width-punctuation table."""
    lines = [
        f"# {title}",
        "",
        f"配對案例數：{summary['n_pairs']}。評分者：{summary['judge']}。"
        "各維度範圍為 1 至 100 分。",
        "統計檢定採雙尾 Wilcoxon 符號等級檢定，並以 Holm 法校正五次檢定。"
        "成對平均差方向為「注入減基準」。",
        "",
        f"| 維度 | {inject_label}（平均±樣本標準差） | "
        f"{baseline_label}（平均±樣本標準差） | 成對平均差 | 勝／同／負 | W | "
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
    parser.add_argument("inject_root", type=Path, help="injection group score root")
    parser.add_argument("baseline_root", type=Path, help=".../multi_rag_off")
    parser.add_argument("--out", type=Path, required=True,
                        help="output directory for the summary files")
    parser.add_argument("--title",
                        default="固定注入無關規則組與 RAG 關閉基準五維度成對比較")
    parser.add_argument("--inject-label", default="注入無關規則")
    parser.add_argument("--baseline-label", default="RAG 關閉基準")
    parser.add_argument("--inject-desc",
                        default="multi_irrelevant_fixed (three fixed irrelevant "
                                "rules injected via extra_rules)")
    parser.add_argument("--baseline-desc",
                        default="multi_rag_off (identical rag-off pipeline, no injection)")
    parser.add_argument("--basename", default="irrelevant_vs_ragoff_quality_summary")
    parser.add_argument("--inject-score-file", default=SCORE_FILE,
                        help="score filename under inject_root")
    parser.add_argument("--baseline-score-file", default=SCORE_FILE,
                        help="score filename under baseline_root; point at a "
                             "re-judged set to pair arms scored in one session")
    args = parser.parse_args()
    summary = relabel(
        summarize(
            load_scores(args.inject_root, args.inject_score_file),
            load_scores(args.baseline_root, args.baseline_score_file),
        ),
        args.inject_desc, args.baseline_desc,
    )
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / f"{args.basename}.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    markdown = render_markdown(summary, args.title, args.inject_label,
                               args.baseline_label)
    (args.out / f"{args.basename}.md").write_text(markdown, encoding="utf-8")
    print(markdown)


if __name__ == "__main__":
    main()
