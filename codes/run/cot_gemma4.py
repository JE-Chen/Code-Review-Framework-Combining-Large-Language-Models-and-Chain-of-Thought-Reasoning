"""Gemma-4 CoT batch runner — replicates the qwen3 crscore++ evaluation.

Mirrors codes/run/cot.py (5-step CoT over the 44 code_to_detect cases,
FAISS RAG threshold 0.7) plus codes/run/crscore_cot.py (the CRSCORE
step_by_step_analysis pass), but drives google/gemma-4-31B-it with the
LoRA at codes/train/outputs-lora-gemma4-31b. Resumable: completed case
folders are skipped on restart.

Run inside the training image (transformers>=5.10 for gemma4):
    docker run --rm --gpus all --ipc host \
        -v <repo>:/workspace -v docker_hf-cache:/workspace/.hf_cache \
        -e PYTHONPATH=/workspace -w /workspace prthinker-gemma4-train \
        bash -c "pip install -q faiss-cpu && python codes/run/cot_gemma4.py"
"""

import datetime
import os
from pathlib import Path

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import torch
from peft import PeftModel
from transformers import AutoModelForImageTextToText, AutoTokenizer

from codes.run.CoT_Prompts.step_by_step_analysis import STEP_BY_STEP_ANALYSIS_TEMPLATE
from prthinker.backends.base import InferenceBackend
from prthinker.pipeline import CoTPipeline
from prthinker.rag import FaissRAGRetriever, NoOpRetriever

# The 2026-06 gemma4 evaluation ran with the qwen-era embedding index
# (Qwen3-Embedding-4B @ 0.7) so its RAG context matches the qwen3 runs
# it is compared against; pin it so reruns stay comparable.
os.environ.setdefault("EMB_MODEL", "Qwen/Qwen3-Embedding-4B")

MODEL_NAME = os.environ.get("MODEL_NAME", "google/gemma-4-31B-it")
LORA_PATH = os.environ.get(
    "LORA_PATH", "/workspace/codes/train/outputs-lora-gemma4-31b"
)
RESULTS_ROOT = Path(
    os.environ.get(
        "RESULTS_ROOT", "/workspace/datas/Results/2026-06-11-gemma4-31b/cot"
    )
)
DATA_ROOT = Path("/workspace/datas/code_to_detect")
# The qwen3 eval ran with max_new_tokens=32768; historical step outputs
# never exceeded ~2K tokens, so 8192 is a runaway guard, not a quality cap.
MAX_NEW_TOKENS = int(os.environ.get("MAX_NEW_TOKENS", 8192))
RAG_ENABLED = os.environ.get("RAG_ENABLED", "1") == "1"

_DATASETS: tuple[tuple[Path, str], ...] = (
    (DATA_ROOT / "bad_data/Python/Copilot", "cot_copilot_bad_data"),
    (DATA_ROOT / "bad_data/Python/ChatGPT", "cot_chatgpt_bad_data"),
    (DATA_ROOT / "code_diff/Python/ChatGPT", "cot_chatgpt_code_diff"),
    (DATA_ROOT / "code_diff/Python/Copilot", "cot_copilot_code_diff"),
    (DATA_ROOT / "only_code/Python/ChatGPT", "cot_chatgpt_only_code"),
    (DATA_ROOT / "only_code/Python/Copilot", "cot_copilot_only_code"),
)

_STEP_FILES = (
    "first_summary_result.md",
    "first_code_review_result.md",
    "linter_result.md",
    "code_smell_result.md",
    "total_summary_result.md",
)


def _log(*parts: object) -> None:
    print(datetime.datetime.now(), *parts, flush=True)


class GemmaLocalBackend(InferenceBackend):
    """Local gemma-4 + LoRA backend, chat-templated like qwen3_ask."""

    def __init__(self, model_name: str, lora_path: str | None) -> None:
        _log("Loading base model", model_name)
        self._tokenizer = AutoTokenizer.from_pretrained(
            model_name, trust_remote_code=True, use_fast=True
        )
        model = AutoModelForImageTextToText.from_pretrained(
            model_name,
            dtype=torch.bfloat16,
            trust_remote_code=True,
            attn_implementation=os.environ.get("ATTN_IMPL", "sdpa"),
            device_map="auto",
        )
        if lora_path:
            _log("Attaching LoRA", lora_path)
            model = PeftModel.from_pretrained(model, lora_path)
        model.eval()
        self._model = model
        self._model_name = model_name

    def generate(
        self,
        prompt: str,
        max_new_tokens: int,
        *,
        cancel_event: "object | None" = None,
    ) -> str:
        del cancel_event  # batch run — no mid-stream cancellation needed
        messages = [{"role": "user", "content": prompt}]
        encoded = self._tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt",
            return_dict=True,
        ).to(self._model.device)
        input_len = encoded["input_ids"].shape[1]
        with torch.no_grad():
            out = self._model.generate(**encoded, max_new_tokens=max_new_tokens)
        if out.shape[1] - input_len >= max_new_tokens:
            _log(f"WARNING: generation hit the {max_new_tokens}-token cap")
        return self._tokenizer.decode(
            out[0][input_len:], skip_special_tokens=True
        ).strip()

    def backend_kind(self) -> str:
        return "local-gemma4"

    def model_name(self) -> str:
        return self._model_name


def _case_done(folder: Path) -> bool:
    return all((folder / name).exists() for name in _STEP_FILES)


def _build_pipeline(backend: InferenceBackend) -> CoTPipeline:
    if RAG_ENABLED:
        retriever = FaissRAGRetriever(threshold=0.7)
    else:
        _log("RAG disabled (RAG_ENABLED=0) — NoOpRetriever")
        retriever = NoOpRetriever()
    return CoTPipeline(
        backend=backend, retriever=retriever, max_new_tokens=MAX_NEW_TOKENS
    )


def run_cot_phase(pipeline: CoTPipeline) -> list[Path]:
    folders: list[Path] = []
    for directory, prefix in _DATASETS:
        files = sorted(f for f in directory.iterdir() if f.is_file())
        for file_path in files:
            folder = RESULTS_ROOT / f"{prefix}_{file_path.stem}"
            folders.append(folder)
            if _case_done(folder):
                _log("skip (done)", folder.name)
                continue
            _log("CoT start", folder.name)
            code = file_path.read_text(encoding="utf-8")
            pipeline.run(code, output_dir=folder)
            _log("CoT done", folder.name)
    return folders


def run_step_by_step_phase(
    backend: InferenceBackend, folders: list[Path]
) -> None:
    for folder in folders:
        out_path = folder / "step_by_step_analysis_result.md"
        if out_path.exists():
            _log("skip (done)", out_path.parent.name, "step_by_step")
            continue
        linter_result = (folder / "linter_result.md").read_text(encoding="utf-8")
        code_smell_result = (folder / "code_smell_result.md").read_text(
            encoding="utf-8"
        )
        prompt = STEP_BY_STEP_ANALYSIS_TEMPLATE.format(
            linter_result=linter_result, code_smell_result=code_smell_result
        )
        _log("step_by_step start", folder.name)
        out_path.write_text(
            backend.generate(prompt, max_new_tokens=MAX_NEW_TOKENS),
            encoding="utf-8",
        )
        _log("step_by_step done", folder.name)


def main() -> None:
    RESULTS_ROOT.mkdir(parents=True, exist_ok=True)
    backend = GemmaLocalBackend(MODEL_NAME, LORA_PATH)
    pipeline = _build_pipeline(backend)
    folders = run_cot_phase(pipeline)
    run_step_by_step_phase(backend, folders)
    _log("All", len(folders), "cases complete")


if __name__ == "__main__":
    main()
