from pathlib import Path

from codes.run.CoT_Prompts.CRSCORE.crscore_llm_as_judge import CRSCore_JUDGE_TEMPLATE
from codes.run.CoT_Prompts.judge import JUDGE_TEMPLATE


def build_llm_judge_prompt(root_folder: str):
    root_path = Path(root_folder)
    for folder_path in root_path.rglob("*"):
        if "cot" in folder_path.name:
            if folder_path.is_dir():
                code_smell_result = None
                linter_result = None
                step_by_step_analysis_result = None
                first_code_review_result = None
                first_summary_result = None
                total_summary_result = None
                for file_path in folder_path.iterdir():
                    if file_path.name == "code_smell_result.md":
                        with open(file_path, "r", encoding="utf-8") as f:
                            code_smell_result = f.read()
                    if file_path.name == "first_code_review_result.md":
                        with open(file_path, "r", encoding="utf-8") as f:
                            first_code_review_result = f.read()
                    if file_path.name == "first_summary_result.md":
                        with open(file_path, "r", encoding="utf-8") as f:
                            first_summary_result = f.read()
                    if file_path.name == "linter_result.md":
                        with open(file_path, "r", encoding="utf-8") as f:
                            linter_result = f.read()
                    if file_path.name == "step_by_step_analysis_result.md":
                        with open(file_path, "r", encoding="utf-8") as f:
                            step_by_step_analysis_result = f.read()
                    if file_path.name == "total_summary_result.md":
                        with open(file_path, "r", encoding="utf-8") as f:
                            total_summary_result = f.read()
                review_comment = "First code review: \n\n" + first_code_review_result + "\n\n" + \
                                 "First summary: \n\n" + first_summary_result + "\n\n" + \
                                 "Total summary: \n\n " + total_summary_result + "\n\n" + \
                                 "Step by step analysis: \n\n" + step_by_step_analysis_result
                judge_prompt = JUDGE_TEMPLATE.format(code_diff="\n\n",
                                                     code_smell_detector_messages=code_smell_result,
                                                     linter_messages=linter_result,
                                                     review_comment=review_comment,
                                                     )
                with open(str(Path(str(folder_path) + "/" + "our_llm_judge.md")), "w+",
                          encoding="utf-8") as f:
                    f.write(judge_prompt)


if __name__ == "__main__":
    target_folder = "./cot"
    build_llm_judge_prompt(target_folder)
