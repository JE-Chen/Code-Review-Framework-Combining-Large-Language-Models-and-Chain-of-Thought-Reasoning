from pathlib import Path

from codes.run.CoT.code_smell_detector import CODE_SMELL_DETECTOR_TEMPLATE
from codes.run.CoT.first_code_review import FIRST_CODE_REVIEW_TEMPLATE
from codes.run.CoT.first_summary_prompt import FIRST_SUMMARY_TEMPLATE
from codes.run.CoT.global_rule import build_global_rule_template
from codes.run.CoT.linter import LINTER_TEMPLATE
from codes.run.CoT.total_summary import TOTAL_SUMMARY_TEMPLATE
from codes.run.ask_functions import get_rag_docs
from codes.util.qwen3_util import load_qwen3_model, qwen3_ask

RUN_ON = "Qwen2.5-Coder"

# 載入 Qwen 的生成模型，用來生成答案
match RUN_ON:
    case "Qwen3.1-7B":
        gen_tokenizer, gen_model = load_qwen3_model(
            model_name="Qwen/Qwen3-1.7B",
            lora_path="../train/outputs-lora-qwen3-1.7b")
    case "Qwen2.5-Coder":
        gen_tokenizer, gen_model = load_qwen3_model(
            model_name="Qwen/Qwen2.5-Coder-7B-Instruct",
            lora_path="../train/outputs-lora-qwen2.5-coder-7b")
    case _:
        gen_tokenizer, gen_model = load_qwen3_model(
            lora_path="../train/outputs-lora-qwen3-30b")

def code_review(code_for_review: str, code_file_path: Path, folder_prefix_name: str):
    folder_path = Path(folder_prefix_name + "_" + str(code_file_path.stem))
    Path.mkdir(folder_path, exist_ok=True)

    if Path(folder_path).is_dir():
        rag_docs = get_rag_docs(prompt=code_for_review, threshold=0.7)

        first_summary = build_global_rule_template(
            prompt=FIRST_SUMMARY_TEMPLATE.format(code_diff=code_for_review),
            rag_rules=rag_docs
        )
        first_summary_result = qwen3_ask(first_summary, gen_tokenizer, gen_model, max_new_tokens=32768)[0]
        with open(str(Path(str(folder_path) + "/" + "first_summary_result.md")), "w", encoding="utf-8") as f:
            f.write(first_summary_result)

        first_code_review = build_global_rule_template(
            prompt=FIRST_CODE_REVIEW_TEMPLATE.format(code_diff=code_for_review),
            rag_rules=rag_docs
        )
        first_code_review_result = qwen3_ask(first_code_review, gen_tokenizer, gen_model, max_new_tokens=32768)[0]
        with open(str(Path(str(folder_path) + "/" + "first_code_review_result.md")), "w", encoding="utf-8") as f:
            f.write(first_code_review_result)

        linter = build_global_rule_template(
            prompt=LINTER_TEMPLATE.format(code_diff=code_for_review),
            rag_rules=rag_docs
        )
        linter_result = qwen3_ask(linter, gen_tokenizer, gen_model, max_new_tokens=32768)[0]
        with open(str(Path(str(folder_path) + "/" + "linter_result.md")), "w", encoding="utf-8") as f:
            f.write(linter_result)

        code_smell = build_global_rule_template(
            prompt=CODE_SMELL_DETECTOR_TEMPLATE.format(code_diff=code_for_review),
            rag_rules=rag_docs
        )
        code_smell_result = qwen3_ask(code_smell, gen_tokenizer, gen_model, max_new_tokens=32768)[0]
        with open(str(Path(str(folder_path) + "/" + "code_smell_result.md")), "w", encoding="utf-8") as f:
            f.write(code_smell_result)

        total_summary = build_global_rule_template(
            prompt=TOTAL_SUMMARY_TEMPLATE.format(
                first_code_review=first_code_review_result,
                first_summary=first_summary_result,
                linter_result=linter_result,
                code_smell_result=code_smell_result,
                code_diff=code,
            ),
            rag_rules=rag_docs)
        total_summary_result = qwen3_ask(total_summary, gen_tokenizer, gen_model, max_new_tokens=32768)[0]
        with open(str(Path(str(folder_path) + "/" + "total_summary_result.md")), "w", encoding="utf-8") as f:
            f.write(total_summary_result)
        print(folder_prefix_name + code_file_path.stem + "  " * 2 + "Generation completed.")

if __name__ == "__main__":
    copilot_bad_data_file_path_list = [f for f in
                                       Path("../../datas/code_to_detect/bad_data/Python/Copilot").iterdir() if
                                       f.is_file()]
    print(copilot_bad_data_file_path_list)

    for file_path in copilot_bad_data_file_path_list:
        with open(file_path, encoding="utf-8") as f:
            code = f.read()
            code_review(code_for_review=code, code_file_path=file_path, folder_prefix_name="cot_copilot_bad_data")

    chatgpt_bad_data_file_path_list = [f for f in
                                       Path("../../datas/code_to_detect/bad_data/Python/ChatGPT").iterdir() if
                                       f.is_file()]
    print(chatgpt_bad_data_file_path_list)

    for file_path in chatgpt_bad_data_file_path_list:
        with open(file_path, encoding="utf-8") as f:
            code = f.read()
            code_review(code_for_review=code, code_file_path=file_path, folder_prefix_name="cot_chatgpt_bad_data")

    chatgpt_code_diff_file_path_list = [f for f in
                                        Path("../../datas/code_to_detect/code_diff/Python/ChatGPT").iterdir() if
                                        f.is_file()]
    print(chatgpt_code_diff_file_path_list)

    for file_path in chatgpt_code_diff_file_path_list:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
            code_review(code_for_review=code, code_file_path=file_path, folder_prefix_name="cot_chatgpt_code_diff")

    copilot_code_diff_file_path_list = [f for f in
                                        Path("../../datas/code_to_detect/code_diff/Python/Copilot").iterdir() if
                                        f.is_file()]
    print(copilot_code_diff_file_path_list)

    for file_path in copilot_code_diff_file_path_list:
        with open(file_path, encoding="utf-8") as f:
            code = f.read()
            code_review(code_for_review=code, code_file_path=file_path, folder_prefix_name="cot_copilot_code_diff")

    chatgpt_only_code_file_path_list = [f for f in
                                        Path("../../datas/code_to_detect/only_code/Python/ChatGPT").iterdir() if
                                        f.is_file()]
    print(chatgpt_only_code_file_path_list)

    for file_path in chatgpt_only_code_file_path_list:
        with open(file_path, encoding="utf-8") as f:
            code = f.read()
            code_review(code_for_review=code, code_file_path=file_path, folder_prefix_name="cot_chatgpt_only_code")

    copilot_only_code_file_path_list = [f for f in
                                        Path("../../datas/code_to_detect/only_code/Python/Copilot").iterdir() if
                                        f.is_file()]
    print(copilot_only_code_file_path_list)

    for file_path in copilot_only_code_file_path_list:
        with open(file_path, encoding="utf-8") as f:
            code = f.read()
            code_review(code_for_review=code, code_file_path=file_path, folder_prefix_name="cot_copilot_only_code")
