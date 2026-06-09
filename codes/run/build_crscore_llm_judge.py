from pathlib import Path

from codes.run.CoT_Prompts.CRSCORE.crscore_llm_as_judge import CRSCore_JUDGE_TEMPLATE

_RESULT_FILES = (
    "code_smell_result.md",
    "linter_result.md",
    "step_by_step_analysis_result.md",
    "first_code_review_result.md",
    "first_summary_result.md",
    "total_summary_result.md",
)


def _read_result_files(folder_path: Path) -> dict[str, str | None]:
    results: dict[str, str | None] = {name: None for name in _RESULT_FILES}
    for file_path in folder_path.iterdir():
        if file_path.name in results:
            with open(file_path, "r", encoding="utf-8") as f:
                results[file_path.name] = f.read()
    return results


def _build_review_comment(results: dict[str, str | None]) -> str:
    return (
        "First code review: \n\n" + results["first_code_review_result.md"] + "\n\n" +
        "First summary: \n\n" + results["first_summary_result.md"] + "\n\n" +
        "Total summary: \n\n " + results["total_summary_result.md"] + "\n\n" +
        "Step by step analysis: \n\n" + results["step_by_step_analysis_result.md"]
    )


def _write_judge_prompt(folder_path: Path, results: dict[str, str | None]) -> None:
    judge_prompt = CRSCore_JUDGE_TEMPLATE.format(
        code_change="\n\n",
        code_smell_detector_messages=results["code_smell_result.md"],
        linter_messages=results["linter_result.md"],
        review_comment=_build_review_comment(results),
    )
    with open(str(Path(str(folder_path) + "/" + "crscore_llm_judge.md")), "w+", encoding="utf-8") as f:
        f.write(judge_prompt)


def build_llm_judge_prompt(root_folder: str):
    root_path = Path(root_folder)
    for folder_path in root_path.rglob("*"):
        if "cot" in folder_path.name and folder_path.is_dir():
            _write_judge_prompt(folder_path, _read_result_files(folder_path))


if __name__ == "__main__":
    target_folder = "./cot"
    build_llm_judge_prompt(target_folder)
