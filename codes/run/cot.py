from pathlib import Path

from codes.run.CoT.code_smell_detector import CODE_SMELL_DETECTOR_TEMPLATE
from codes.run.CoT.first_code_review import FIRST_CODE_REVIEW_TEMPLATE
from codes.run.CoT.first_summary_prompt import FIRST_SUMMARY_TEMPLATE
from codes.run.CoT.global_rule import build_global_rule_template, GLOBAL_RULE_TEMPLATE
from codes.run.CoT.linter import LINTER_TEMPLATE
from codes.run.CoT.total_summary import TOTAL_SUMMARY_TEMPLATE
from codes.run.ask_functions import rag_ask

def code_review(code_for_review: str, code_file_path: Path):

    Path.mkdir(Path(str(code_file_path.name)), exist_ok=True)

    if Path(str(code_file_path.name)).is_dir():

        first_summary = build_global_rule_template(prompt=FIRST_SUMMARY_TEMPLATE.format(code_diff=code_for_review))
        first_summary_result = rag_ask(first_summary, "first_summary")
        with open(str(code_file_path.name) + "_" + "first_summary_result.md", "w", encoding="utf-8") as f:
            f.write(first_summary_result)

        first_code_review = build_global_rule_template(prompt=FIRST_CODE_REVIEW_TEMPLATE.format(code_diff=code_for_review))
        first_code_review_result = rag_ask(first_code_review, "first_code_review")
        with open(str(code_file_path.name) + "_" + "first_code_review_result.md", "w", encoding="utf-8") as f:
            f.write(first_code_review_result)

        linter = build_global_rule_template(prompt=LINTER_TEMPLATE.format(code_diff=code_for_review))
        linter_result = rag_ask(linter, "linter")
        with open(str(code_file_path.name) + "_" + "linter_result.md", "w", encoding="utf-8") as f:
            f.write(linter_result)

        code_smell = build_global_rule_template(prompt=CODE_SMELL_DETECTOR_TEMPLATE.format(code_diff=code_for_review))
        code_smell_result = rag_ask(code_smell, "code_smell")
        with open(str(code_file_path.name) + "_" + "code_smell_result.md", "w", encoding="utf-8") as f:
            f.write(code_smell_result)

        total_summary = build_global_rule_template(prompt=TOTAL_SUMMARY_TEMPLATE.format(
            first_code_review=first_code_review,
            first_summary=first_summary,
            code_diff=code_smell,
        ))
        total_summary_result = rag_ask(total_summary, "total_summary")
        with open(str(code_file_path.name) + "_" + "total_summary_result.md", "w", encoding="utf-8") as f:
            f.write(total_summary_result)

chatgpt_code_diff_file_path_list = [f for f in
                                    Path("../../datas/code-to-detect/code_diff/Python/ChatGPT").iterdir() if f.is_file()]
print(chatgpt_code_diff_file_path_list)

for file_path in chatgpt_code_diff_file_path_list:
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()
        code_review(code_for_review=code, code_file_path=file_path)

copilot_code_diff_file_path_list = [f for f in
                                    Path("../../datas/code-to-detect/code_diff/Python/Copilot").iterdir() if f.is_file()]
print(copilot_code_diff_file_path_list)

for file_path in copilot_code_diff_file_path_list:
    with open(file_path, encoding="utf-8") as f:
        code = f.read()
        code_review(code_for_review=code, code_file_path=file_path)

chatgpt_only_code_file_path_list = [f for f in
                                    Path("../../datas/code-to-detect/only_code/Python/ChatGPT").iterdir() if f.is_file()]
print(chatgpt_only_code_file_path_list)

for file_path in chatgpt_only_code_file_path_list:
    with open(file_path, encoding="utf-8") as f:
        code = f.read()
        code_review(code_for_review=code, code_file_path=file_path)

copilot_only_code_file_path_list = [f for f in
                                    Path("../../datas/code-to-detect/only_code/Python/Copilot").iterdir() if f.is_file()]
print(copilot_only_code_file_path_list)

for file_path in copilot_only_code_file_path_list:
    with open(file_path, encoding="utf-8") as f:
        code = f.read()
        code_review(code_for_review=code, code_file_path=file_path)
