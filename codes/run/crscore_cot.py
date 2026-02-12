import datetime
import time
from pathlib import Path

from codes.run.CoT.step_by_step_analysis import STEP_BY_STEP_ANALYSIS_TEMPLATE
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


def list_and_ask_qwen(root_folder: str):
    root_path = Path(root_folder)
    for folder_path in root_path.rglob("*"):
        if "cot" in folder_path.name or "skills" in folder_path.name:
            if folder_path.is_dir():
                code_smell_result = None
                linter_result = None
                for file_path in folder_path.iterdir():
                    if file_path.is_file() and file_path.name in (
                            "code_smell_result.md", "linter_result.md"
                    ):
                        if file_path.name == "code_smell_result.md":
                            with open(file_path, "r", encoding="utf-8") as f:
                                code_smell_result = f.read()
                        if file_path.name == "linter_result.md":
                            with open(file_path, "r", encoding="utf-8") as f:
                                linter_result = f.read()
                step_by_step_analysis = STEP_BY_STEP_ANALYSIS_TEMPLATE.format(
                    linter_result=linter_result,
                    code_smell_result=code_smell_result
                )
                step_by_step_analysis_result = qwen3_ask(
                    step_by_step_analysis, gen_tokenizer, gen_model, max_new_tokens=32768)[0]
                with open(str(Path(str(folder_path) + "/" + "step_by_step_analysis_result.md")), "w",
                          encoding="utf-8") as f:
                    f.write(step_by_step_analysis_result)
                print(
                    f"Folder: {folder_path.absolute()}'s step_by_step_analysis_result "
                    f"generation done {datetime.datetime.now()}"
                )


if __name__ == "__main__":
    target_folder = "./cot"
    list_and_ask_qwen(target_folder)
