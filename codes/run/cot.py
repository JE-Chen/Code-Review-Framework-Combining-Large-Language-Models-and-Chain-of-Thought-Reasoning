from pathlib import Path

from codes.run.CoT.code_smell_detector import CODE_SMELL_DETECTOR_TEMPLATE
from codes.run.CoT.first_code_review import FIRST_CODE_REVIEW_TEMPLATE
from codes.run.CoT.first_summary_prompt import FIRST_SUMMARY_TEMPLATE
from codes.run.CoT.global_rule import build_global_rule_template, GLOBAL_RULE_TEMPLATE
from codes.run.CoT.linter import LINTER_TEMPLATE
from codes.run.CoT.total_summary import TOTAL_SUMMARY_TEMPLATE
from codes.run.ask_functions import get_rag_docs
from codes.util.qwen3_util import load_qwen3_model, qwen3_ask

# 載入 Qwen 的生成模型，用來生成答案
gen_tokenizer, gen_model = load_qwen3_model()


def code_review(code_for_review: str, code_file_path: Path):
    Path.mkdir(Path(str(code_file_path.name)), exist_ok=True)

    if Path(str(code_file_path.name)).is_dir():
        rag_docs = get_rag_docs(prompt=code_for_review, threshold=0.7)

        first_summary = build_global_rule_template(
            prompt=FIRST_SUMMARY_TEMPLATE.format(code_diff=code_for_review),
            rag_rules=rag_docs
        )
        result = qwen3_ask("", first_summary, gen_tokenizer, gen_model, max_new_tokens=32768)[0]
        with open(str(code_file_path.name) + "_" + "first_summary_result.md", "w", encoding="utf-8") as f:
            f.write(result)

        first_code_review = build_global_rule_template(
            prompt=FIRST_CODE_REVIEW_TEMPLATE.format(code_diff=code_for_review),
            rag_rules=rag_docs
        )
        result = qwen3_ask("", first_code_review, gen_tokenizer, gen_model, max_new_tokens=32768)[0]
        with open(str(code_file_path.name) + "_" + "first_code_review_result.md", "w", encoding="utf-8") as f:
            f.write(result)

        linter = build_global_rule_template(
            prompt=LINTER_TEMPLATE.format(code_diff=code_for_review),
            rag_rules=rag_docs
        )
        result = qwen3_ask("", linter, gen_tokenizer, gen_model, max_new_tokens=32768)[0]
        with open(str(code_file_path.name) + "_" + "linter_result.md", "w", encoding="utf-8") as f:
            f.write(result)

        code_smell = build_global_rule_template(
            prompt=CODE_SMELL_DETECTOR_TEMPLATE.format(code_diff=code_for_review),
            rag_rules=rag_docs
        )
        result = qwen3_ask("", code_smell, gen_tokenizer, gen_model, max_new_tokens=32768)[0]
        with open(str(code_file_path.name) + "_" + "code_smell_result.md", "w", encoding="utf-8") as f:
            f.write(result)

        total_summary = build_global_rule_template(
            prompt=TOTAL_SUMMARY_TEMPLATE.format(
                first_code_review=first_code_review,
                first_summary=first_summary,
                code_diff=code_smell,
            ),
            rag_rules=rag_docs)
        result = qwen3_ask("", total_summary, gen_tokenizer, gen_model, max_new_tokens=32768)[0]
        with open(str(code_file_path.name) + "_" + "total_summary_result.md", "w", encoding="utf-8") as f:
            f.write(result)


chatgpt_code_diff_file_path_list = [f for f in
                                    Path("../../datas/code_to_detect/code_diff/Python/ChatGPT").iterdir() if
                                    f.is_file()]
print(chatgpt_code_diff_file_path_list)

for file_path in chatgpt_code_diff_file_path_list:
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()
        code_review(code_for_review=code, code_file_path=file_path)

copilot_code_diff_file_path_list = [f for f in
                                    Path("../../datas/code_to_detect/code_diff/Python/Copilot").iterdir() if
                                    f.is_file()]
print(copilot_code_diff_file_path_list)

for file_path in copilot_code_diff_file_path_list:
    with open(file_path, encoding="utf-8") as f:
        code = f.read()
        code_review(code_for_review=code, code_file_path=file_path)

chatgpt_only_code_file_path_list = [f for f in
                                    Path("../../datas/code_to_detect/only_code/Python/ChatGPT").iterdir() if
                                    f.is_file()]
print(chatgpt_only_code_file_path_list)

for file_path in chatgpt_only_code_file_path_list:
    with open(file_path, encoding="utf-8") as f:
        code = f.read()
        code_review(code_for_review=code, code_file_path=file_path)

copilot_only_code_file_path_list = [f for f in
                                    Path("../../datas/code_to_detect/only_code/Python/Copilot").iterdir() if
                                    f.is_file()]
print(copilot_only_code_file_path_list)

for file_path in copilot_only_code_file_path_list:
    with open(file_path, encoding="utf-8") as f:
        code = f.read()
        code_review(code_for_review=code, code_file_path=file_path)
