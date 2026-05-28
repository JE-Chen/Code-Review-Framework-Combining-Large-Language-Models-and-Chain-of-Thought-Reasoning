"""Remote HTTP backends.

Two thin clients of the FastAPI server:

- RemoteHttpBackend       - proxies a single prompt to /ask.
                            Plugs into CoTPipeline like LocalQwen3Backend,
                            so the pipeline orchestration stays on the runner.

- RemotePipelineClient    - calls /review once and gets the full structured
                            result. Saves N-1 HTTP round-trips per review
                            and lets the server own RAG + step orchestration.
                            Not an InferenceBackend (it returns ReviewResponse,
                            not a raw string).
"""

from __future__ import annotations

import httpx

from reviewmind.backends.base import InferenceBackend
from reviewmind.config import RemoteBackendConfig
from reviewmind.schemas import ReviewRequest, ReviewResponse


def _build_client(config: RemoteBackendConfig) -> httpx.Client:
    headers: dict[str, str] = {}
    if config.api_key:
        headers["Authorization"] = f"Bearer {config.api_key}"
    return httpx.Client(
        base_url=config.url.rstrip("/"),
        timeout=config.timeout_seconds,
        headers=headers,
    )


class RemoteHttpBackend(InferenceBackend):
    """POSTs prompts to `/ask` (plain text out)."""

    def __init__(self, config: RemoteBackendConfig) -> None:
        self._config = config
        self._client = _build_client(config)

    def backend_kind(self) -> str:
        return "remote"

    def model_name(self) -> str:
        # The server picks the model at boot time; the runner does not know it.
        return "remote"

    def generate(self, prompt: str, max_new_tokens: int) -> str:
        response = self._client.post(
            "/ask",
            json={"prompt": prompt, "max_new_tokens": max_new_tokens},
        )
        response.raise_for_status()
        return response.text

    def close(self) -> None:
        self._client.close()


class RemotePipelineClient:
    """One-shot caller of `/review` — server runs RAG + every step.

    Use this when you trust the server to own the orchestration. The
    response is structured, including any inline findings.
    """

    def __init__(self, config: RemoteBackendConfig) -> None:
        self._config = config
        self._client = _build_client(config)

    def review(self, request: ReviewRequest) -> ReviewResponse:
        response = self._client.post(
            "/review",
            json=request.model_dump(),
        )
        response.raise_for_status()
        return ReviewResponse.model_validate_json(response.text)

    def close(self) -> None:
        self._client.close()
