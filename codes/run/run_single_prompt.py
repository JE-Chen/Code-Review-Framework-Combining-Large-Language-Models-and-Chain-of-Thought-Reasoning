from pathlib import Path

from codes.run.singel_prompt import SINGLE_CODE_REVIEW_PROMPT
from codes.util.qwen3_util import load_qwen3_model, qwen3_ask

RUN_ON = "Qwen/Qwen3-Coder-30B-A3B-Instruct"

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
    case "Qwen/Qwen3-Coder-30B-A3B-Instruct":
        gen_tokenizer, gen_model = load_qwen3_model(
            model_name="Qwen/Qwen3-Coder-30B-A3B-Instruct",
            lora_path="../train/outputs-lora-qwen3-coder-30b")
    case _:
        gen_tokenizer, gen_model = load_qwen3_model(
            lora_path="../train/outputs-lora-qwen3-30b")


def code_review(code_for_review: str, code_file_path: Path, folder_prefix_name: str):
    folder_path = Path(folder_prefix_name + "_" + str(code_file_path.stem))
    Path.mkdir(folder_path, exist_ok=True)

    if Path(folder_path).is_dir():
        single_code_review_prompt = SINGLE_CODE_REVIEW_PROMPT.format(code_diff=code_for_review)
        single_code_review_prompt_result = \
            qwen3_ask(single_code_review_prompt, gen_tokenizer, gen_model, max_new_tokens=32768)[0]
        with open(str(Path(str(folder_path) + "/" + "single_code_review_prompt_result.md")), "w",
                  encoding="utf-8") as f:
            f.write(single_code_review_prompt_result)


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
