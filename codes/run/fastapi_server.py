from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import PlainTextResponse

from codes.util.qwen3_util import load_qwen3_model, qwen3_ask

RUN_ON = "Qwen/Qwen3-Coder-30B-A3B-Instruct"

app = FastAPI()


class PromptRequest(BaseModel):
    prompt: str


# -------------------------
# Load Model (only once)
# -------------------------

match RUN_ON:
    case "Qwen3.1-7B":
        gen_tokenizer, gen_model = load_qwen3_model(
            model_name="Qwen/Qwen3-1.7B",
            lora_path="../train/outputs-lora-qwen3-1.7b"
        )

    case "Qwen2.5-Coder":
        gen_tokenizer, gen_model = load_qwen3_model(
            model_name="Qwen/Qwen2.5-Coder-7B-Instruct",
            lora_path="../train/outputs-lora-qwen2.5-coder-7b"
        )

    case "Qwen/Qwen3-Coder-30B-A3B-Instruct":
        gen_tokenizer, gen_model = load_qwen3_model(
            model_name="Qwen/Qwen3-Coder-30B-A3B-Instruct",
            lora_path="../train/outputs-lora-qwen3-coder-30b"
        )

    case _:
        gen_tokenizer, gen_model = load_qwen3_model(
            lora_path="../train/outputs-lora-qwen3-30b"
        )


# -------------------------
# API
# -------------------------

@app.post("/ask", response_class=PlainTextResponse)
def ask_llm(req: PromptRequest):

    result = qwen3_ask(
        req.prompt,
        gen_tokenizer,
        gen_model,
        max_new_tokens=32768
    )[0]

    return result