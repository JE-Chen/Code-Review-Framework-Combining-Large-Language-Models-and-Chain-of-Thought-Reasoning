import datetime

import torch
import transformers
from transformers import AutoTokenizer, pipeline
import os

from codes.util.memory import get_max_memory

os.environ["PYTORCH_ALLOC_CONF"] = "expandable_segments:True"


def load_llama3_model():
    model_id = "meta-llama/Llama-3.1-8B-Instruct"

    # === 一次載入 tokenizer 與模型 ===
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_id)

    print("Loading model across all GPUs...")
    max_memory = get_max_memory()

    llm_pipeline = transformers.pipeline(
        "text-generation",
        model="meta-llama/Llama-3.1-8B-Instruct",
        device_map="auto",
        model_kwargs={
            "torch_dtype": torch.bfloat16,
            "max_memory": max_memory,
        }
    )
    print(datetime.datetime.now(), "Model loaded")
    return llm_pipeline, tokenizer


def llama3_ask(system_prompt: str, question_prompt: str, llm_pipeline):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question_prompt},
    ]

    outputs = llm_pipeline(
        messages,
        max_new_tokens=2048,
    )
    print(datetime.datetime.now(), "Generate done")
    return outputs
