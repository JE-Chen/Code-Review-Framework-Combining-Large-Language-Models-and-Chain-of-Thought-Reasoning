"""CoT batch runner.

Thin wrapper over the `prthinker` package: loads the model once, then
iterates over every file in the standard test-data directories and writes
per-step outputs to `<prefix>_<stem>/`.
"""

import os
from pathlib import Path

from prthinker.backends.local import LocalQwen3Backend
from prthinker.config import LocalBackendConfig
from prthinker.pipeline import CoTPipeline
from prthinker.rag import FaissRAGRetriever

RUN_ON = "Qwen/Qwen3-Coder-30B-A3B-Instruct"

# The qwen evaluation results were produced with the qwen-era embedding
# index (Qwen3-Embedding-4B @ 0.7); pin it so reruns stay comparable.
os.environ.setdefault("EMB_MODEL", "Qwen/Qwen3-Embedding-4B")

_LORA_BY_MODEL: dict[str, str] = {
    "Qwen/Qwen3-1.7B": "../train/outputs-lora-qwen3-1.7b",
    "Qwen/Qwen2.5-Coder-7B-Instruct": "../train/outputs-lora-qwen2.5-coder-7b",
    "Qwen/Qwen3-Coder-30B-A3B-Instruct": "../train/outputs-lora-qwen3-coder-30b",
}
_DEFAULT_LORA = "../train/outputs-lora-qwen3-30b"


def _build_pipeline() -> CoTPipeline:
    lora = _LORA_BY_MODEL.get(RUN_ON, _DEFAULT_LORA)
    backend = LocalQwen3Backend(LocalBackendConfig(model_name=RUN_ON, lora_path=lora))
    retriever = FaissRAGRetriever(threshold=0.7)
    return CoTPipeline(backend=backend, retriever=retriever)


def code_review(
    pipeline: CoTPipeline,
    code_for_review: str,
    code_file_path: Path,
    folder_prefix_name: str,
) -> None:
    folder_path = Path(f"{folder_prefix_name}_{code_file_path.stem}")
    pipeline.run(code_for_review, output_dir=folder_path)
    print(f"{folder_prefix_name}{code_file_path.stem}  Generation completed.")


_DATASETS: tuple[tuple[str, str], ...] = (
    ("../../datas/code_to_detect/bad_data/Python/Copilot", "cot_copilot_bad_data"),
    ("../../datas/code_to_detect/bad_data/Python/ChatGPT", "cot_chatgpt_bad_data"),
    ("../../datas/code_to_detect/code_diff/Python/ChatGPT", "cot_chatgpt_code_diff"),
    ("../../datas/code_to_detect/code_diff/Python/Copilot", "cot_copilot_code_diff"),
    ("../../datas/code_to_detect/only_code/Python/ChatGPT", "cot_chatgpt_only_code"),
    ("../../datas/code_to_detect/only_code/Python/Copilot", "cot_copilot_only_code"),
)


def main() -> None:
    pipeline = _build_pipeline()
    for dir_str, prefix in _DATASETS:
        directory = Path(dir_str)
        files = [f for f in directory.iterdir() if f.is_file()]
        print(files)
        for file_path in files:
            code = file_path.read_text(encoding="utf-8")
            code_review(pipeline, code, file_path, prefix)


if __name__ == "__main__":
    main()
