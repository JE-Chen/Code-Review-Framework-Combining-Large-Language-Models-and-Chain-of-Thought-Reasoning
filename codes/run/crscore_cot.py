import datetime
from pathlib import Path

from codes.run.CoT_Prompts.step_by_step_analysis import STEP_BY_STEP_ANALYSIS_TEMPLATE
from codes.util.hf_model_util import load_hf_model, hf_generate

RUN_ON = "Qwen/Qwen3-Coder-30B-A3B-Instruct"

# 載入 Qwen 的生成模型，用來生成答案
match RUN_ON:
    case "Qwen3.1-7B":
        gen_tokenizer, gen_model = load_hf_model(
            model_name="Qwen/Qwen3-1.7B",
            lora_path="../train/outputs-lora-qwen3-1.7b")
    case "Qwen2.5-Coder":
        gen_tokenizer, gen_model = load_hf_model(
            model_name="Qwen/Qwen2.5-Coder-7B-Instruct",
            lora_path="../train/outputs-lora-qwen2.5-coder-7b")
    case "Qwen/Qwen3-Coder-30B-A3B-Instruct":
        gen_tokenizer, gen_model = load_hf_model(
            model_name="Qwen/Qwen3-Coder-30B-A3B-Instruct")
    case _:
        gen_tokenizer, gen_model = load_hf_model(
            lora_path="../train/outputs-lora-qwen3-30b")


def _read_inputs(folder_path: Path) -> tuple[str | None, str | None]:
    results: dict[str, str | None] = {
        "code_smell_result.md": None,
        "linter_result.md": None,
    }
    for file_path in folder_path.iterdir():
        if file_path.is_file() and file_path.name in results:
            with open(file_path, "r", encoding="utf-8") as f:
                results[file_path.name] = f.read()
    return results["code_smell_result.md"], results["linter_result.md"]


def _process_folder(folder_path: Path) -> None:
    code_smell_result, linter_result = _read_inputs(folder_path)
    step_by_step_analysis = STEP_BY_STEP_ANALYSIS_TEMPLATE.format(
        linter_result=linter_result,
        code_smell_result=code_smell_result
    )
    step_by_step_analysis_result = hf_generate(
        step_by_step_analysis, gen_tokenizer, gen_model, max_new_tokens=32768)[0]
    with open(str(Path(str(folder_path) + "/" + "step_by_step_analysis_result.md")), "w",
              encoding="utf-8") as f:
        f.write(step_by_step_analysis_result)
    print(
        f"Folder: {folder_path.absolute()}'s step_by_step_analysis_result "
        f"generation done {datetime.datetime.now()}"
    )


def list_and_ask_qwen(root_folder: str):
    root_path = Path(root_folder)
    for folder_path in root_path.rglob("*"):
        if "cot" in folder_path.name and folder_path.is_dir():
            _process_folder(folder_path)


if __name__ == "__main__":
    target_folder = "./cot"
    list_and_ask_qwen(target_folder)
