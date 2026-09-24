"""Aggregate compatible coverage.json and precision.json objective scores.

Environment:
  EXP_ROOT          experiment directory
  CONDITION         condition under EXP_ROOT, default multi_rag_on
  GT_ROOT           frozen ground-truth directory
  CONTROL_EXP_ROOT  optional comparison experiment directory
  CONTROL_CONDITION optional comparison condition, default multi_rag_on
"""
import json
import os
from collections import Counter
from pathlib import Path


REPO = Path(__file__).resolve().parents[4]
EXP = Path(os.environ.get(
    "EXP_ROOT", REPO / "datas" / "Results" / "2026-07-20-gemma4-rag-calibrated"
))
CONDITION = os.environ.get("CONDITION", "multi_rag_on")
GT_ROOT = Path(os.environ.get(
    "GT_ROOT", REPO / "datas" / "Results" / "2026-07-19-gemma4-experiment" / "ground_truth"
))
CONTROL_ROOT_TEXT = os.environ.get("CONTROL_EXP_ROOT", "")
CONTROL_ROOT = Path(CONTROL_ROOT_TEXT) if CONTROL_ROOT_TEXT else None
CONTROL_CONDITION = os.environ.get("CONTROL_CONDITION", "multi_rag_on")
WEIGHTS = {"critical": 4, "high": 3, "medium": 2, "low": 1}


def safe_div(numerator, denominator):
    return numerator / denominator if denominator else 0.0


def case_dirs(root, condition):
    folder = root / condition / "cot"
    return {p.name: p for p in folder.iterdir() if p.is_dir()} if folder.exists() else {}


def load_scores(case_dir):
    coverage = json.loads((case_dir / "coverage.json").read_text(encoding="utf-8"))
    precision = json.loads((case_dir / "precision.json").read_text(encoding="utf-8"))
    return coverage, precision


def aggregate(root, condition):
    totals = Counter()
    category_total = Counter()
    category_covered = Counter()
    per_case = {}
    missing = []
    for gt_path in sorted(GT_ROOT.glob("*.json")):
        case = gt_path.stem
        case_dir = root / condition / "cot" / case
        if not (case_dir / "coverage.json").exists() or not (case_dir / "precision.json").exists():
            missing.append(case)
            continue
        reference = json.loads(gt_path.read_text(encoding="utf-8"))
        by_id = {item["id"]: item for item in reference}
        coverage, precision = load_scores(case_dir)
        covered = set(coverage["covered_ids"])
        unknown = covered - set(by_id)
        if unknown:
            raise ValueError(f"{case}: unknown covered IDs {sorted(unknown)}")
        totals["cases"] += 1
        totals["issues"] += len(reference)
        totals["covered"] += len(covered)
        totals["claims"] += int(precision["claims"])
        totals["valid"] += int(precision["valid"])
        for item in reference:
            category_total[item["category"]] += 1
            weight = WEIGHTS[item["severity"]]
            totals["severity_total"] += weight
            if item["id"] in covered:
                category_covered[item["category"]] += 1
                totals["severity_covered"] += weight
        per_case[case] = {
            "covered": len(covered),
            "issues": len(reference),
            "recall": safe_div(len(covered), len(reference)),
            "claims": int(precision["claims"]),
            "valid": int(precision["valid"]),
        }
    recall = safe_div(totals["covered"], totals["issues"])
    precision = safe_div(totals["valid"], totals["claims"])
    result = {
        "experiment": str(root),
        "condition": condition,
        "completed_cases": totals["cases"],
        "missing_cases": missing,
        "covered": totals["covered"],
        "issues": totals["issues"],
        "recall": recall,
        "valid": totals["valid"],
        "claims": totals["claims"],
        "precision": precision,
        "f1": safe_div(2 * precision * recall, precision + recall),
        "severity_weighted_recall": safe_div(
            totals["severity_covered"], totals["severity_total"]
        ),
        "per_category": {
            category: {
                "covered": category_covered[category],
                "total": total,
                "recall": safe_div(category_covered[category], total),
            }
            for category, total in sorted(category_total.items())
        },
        "per_case": per_case,
    }
    return result


def main():
    result = aggregate(EXP, CONDITION)
    if CONTROL_ROOT:
        control = aggregate(CONTROL_ROOT, CONTROL_CONDITION)
        wins = Counter()
        for case in sorted(set(result["per_case"]) & set(control["per_case"])):
            delta = result["per_case"][case]["recall"] - control["per_case"][case]["recall"]
            wins["higher" if delta > 0 else "lower" if delta < 0 else "equal"] += 1
        result["control"] = {
            key: value for key, value in control.items() if key != "per_case"
        }
        result["paired_case_recall"] = dict(wins)
    output = EXP / f"objective_summary_{CONDITION}.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "per_case"},
                     ensure_ascii=False, indent=2))
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
