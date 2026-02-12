from Skills.code_review import CODE_REVIEW_SKILL_TEMPLATE
from Skills.code_explainer import CODE_EXPLAINER_TEMPLATE
from pathlib import Path

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

rag_prompt = """
{rag_rules_section}

{prompt}
"""

def build_rag_string(rag_rules=None, prompt=""):
    if not rag_rules:
        rag_rules_section = ""
    elif isinstance(rag_rules, list):
        # 每條 rule 一行（你也可以改成編號）
        rag_rules_section = "".join(str(rule) for rule in rag_rules)
    else:
        rag_rules_section = str(rag_rules)

    return rag_prompt.format(
        rag_rules_section=rag_rules_section,
        prompt=prompt
    )



def ai_response(code_for_review: str, code_file_path: Path, folder_prefix_name: str):
    folder_path = Path(folder_prefix_name + "_" + str(code_file_path.stem))
    Path.mkdir(folder_path, exist_ok=True)

    rag_docs = get_rag_docs(code_for_review)

    code_explainer_prompt = build_rag_string(
        prompt=CODE_EXPLAINER_TEMPLATE.format(code_diff=code_for_review),
        rag_rules=rag_docs
    )
    print(code_explainer_prompt)
    result = qwen3_ask(code_explainer_prompt, gen_tokenizer, gen_model, max_new_tokens=32768)[0]

    with open(str(Path(str(folder_path) + "/" + "code_explainer.md")), "w", encoding="utf-8") as f:
        f.write(result)

    rag_docs = get_rag_docs(code_for_review)

    code_review_prompt = build_rag_string(
        prompt=CODE_REVIEW_SKILL_TEMPLATE.format(code_diff=code_for_review),
        rag_rules=rag_docs
    )

    print(code_review_prompt)

    result = qwen3_ask(code_review_prompt, gen_tokenizer, gen_model, max_new_tokens=32768)[0]
    with open(str(Path(str(folder_path) + "/" + "code_review.md")), "w", encoding="utf-8") as f:
        f.write(result)

if __name__ == "__main__":

    copilot_bad_data_file_path_list = [f for f in
                                        Path("../../datas/code_to_detect/bad_data/Python/Copilot").iterdir() if
                                        f.is_file()]
    print(copilot_bad_data_file_path_list)

    for file_path in copilot_bad_data_file_path_list:
        with open(file_path, encoding="utf-8") as f:
            code = f.read()
            ai_response(code_for_review=code, code_file_path=file_path, folder_prefix_name="skills_copilot_bad_data")

    chatgpt_bad_data_file_path_list = [f for f in
                                        Path("../../datas/code_to_detect/bad_data/Python/ChatGPT").iterdir() if
                                        f.is_file()]
    print(chatgpt_bad_data_file_path_list)

    for file_path in chatgpt_bad_data_file_path_list:
        with open(file_path, encoding="utf-8") as f:
            code = f.read()
            ai_response(code_for_review=code, code_file_path=file_path, folder_prefix_name="skills_chatgpt_bad_data")

    chatgpt_code_diff_file_path_list = [f for f in
                                        Path("../../datas/code_to_detect/code_diff/Python/ChatGPT").iterdir() if
                                        f.is_file()]
    print(chatgpt_code_diff_file_path_list)

    for file_path in chatgpt_code_diff_file_path_list:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
            ai_response(code_for_review=code, code_file_path=file_path, folder_prefix_name="skills_chatgpt_code_diff")

    copilot_code_diff_file_path_list = [f for f in
                                        Path("../../datas/code_to_detect/code_diff/Python/Copilot").iterdir() if
                                        f.is_file()]
    print(copilot_code_diff_file_path_list)

    for file_path in copilot_code_diff_file_path_list:
        with open(file_path, encoding="utf-8") as f:
            code = f.read()
            ai_response(code_for_review=code, code_file_path=file_path, folder_prefix_name="skills_copilot_code_diff")

    chatgpt_only_code_file_path_list = [f for f in
                                        Path("../../datas/code_to_detect/only_code/Python/ChatGPT").iterdir() if
                                        f.is_file()]
    print(chatgpt_only_code_file_path_list)

    for file_path in chatgpt_only_code_file_path_list:
        with open(file_path, encoding="utf-8") as f:
            code = f.read()
            ai_response(code_for_review=code, code_file_path=file_path, folder_prefix_name="skills_chatgpt_only_code")

    copilot_only_code_file_path_list = [f for f in
                                        Path("../../datas/code_to_detect/only_code/Python/Copilot").iterdir() if
                                        f.is_file()]
    print(copilot_only_code_file_path_list)

    for file_path in copilot_only_code_file_path_list:
        with open(file_path, encoding="utf-8") as f:
            code = f.read()
            ai_response(code_for_review=code, code_file_path=file_path, folder_prefix_name="skills_copilot_only_code")
