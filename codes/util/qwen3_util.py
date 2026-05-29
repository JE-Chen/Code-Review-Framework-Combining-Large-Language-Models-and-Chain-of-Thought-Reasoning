import datetime

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    StoppingCriteria,
    StoppingCriteriaList,
)
from peft import PeftModel

from prthinker.pipeline import ReviewCancelledError


class _CancelStoppingCriteria(StoppingCriteria):
    """Stops generation when ``cancel_event`` flips. Polled every token
    so cancellation lands within ~one token (~50-100ms on L40S)."""

    def __init__(self, cancel_event):
        super().__init__()
        self._cancel_event = cancel_event

    def __call__(self, input_ids, scores, **kwargs):
        return (
            self._cancel_event is not None
            and self._cancel_event.is_set()
        )


def load_qwen3_model(lora_path: str = None, model_name: str = "Qwen/Qwen3-30B-A3B-Thinking-2507", quantization: bool = True):

    print("Loading model across all GPUs...")
    if model_name in ["Qwen/Qwen3-30B-A3B-Thinking-2507", "Qwen/Qwen3-Coder-30B-A3B-Instruct"]:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,  # bf16 compute if supported
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            quantization_config=bnb_config,
        )
    elif not quantization:
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
        )
    else:
        bnb_config = BitsAndBytesConfig(
            load_in_8bit=True,
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            quantization_config=bnb_config,
        )

    print(datetime.datetime.now(), "Model loaded")

    # === 一次載入模型與 tokenizer ===
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    if lora_path:
        model = PeftModel.from_pretrained(model, lora_path)
        print(datetime.datetime.now(), "LoRa loaded")

    return model, tokenizer

def qwen3_ask(prompt: str, model, tokenizer, max_new_tokens: int = 16784, cancel_event=None):
    messages = [
        {"role": "user", "content": prompt}
    ]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    stopping_criteria = None
    if cancel_event is not None:
        stopping_criteria = StoppingCriteriaList(
            [_CancelStoppingCriteria(cancel_event)]
        )

    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=max_new_tokens,
        stopping_criteria=stopping_criteria,
    )

    # If the stopping criterion fired because the cancel_event was set,
    # bail out before decoding — the partial output is useless to the
    # caller and the worker's exception handler needs to see this as a
    # cancellation, not a truncated success.
    if cancel_event is not None and cancel_event.is_set():
        raise ReviewCancelledError(
            "Generation interrupted mid-stream by cancel_event"
        )

    output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()

    try:
        index = len(output_ids) - output_ids[::-1].index(151668)
    except ValueError:
        index = 0

    thinking_content = tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
    content = tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")
    print(datetime.datetime.now(), "Generation completed.")
    return content, thinking_content

