"""Accumulate provider-reported usage while preserving unknown measurements."""

from dataclasses import asdict, is_dataclass
from urllib.parse import urlsplit, urlunsplit

from prthinker.backends.base import InferenceBackend
from prthinker.pricing import estimate_cost
from prthinker.redaction import redact


def public_configuration(value):
    """Archive resolved settings without keys, credentials or URL query data."""
    if is_dataclass(value):
        value = asdict(value)
    if isinstance(value, dict):
        return {key: public_configuration(item) for key, item in value.items()
                if not _secret_key(key)}
    if isinstance(value, (list, tuple)):
        return [public_configuration(item) for item in value]
    if isinstance(value, str):
        if "://" in value:
            parts = urlsplit(value)
            host = parts.hostname or ""
            if ":" in host:
                host = "[" + host + "]"
            if parts.port:
                host += ":" + str(parts.port)
            value = urlunsplit((parts.scheme, host, parts.path, "", ""))
        return redact(value)[0]
    if value is None or isinstance(value, (int, float, bool)):
        return value
    return str(value)


def _secret_key(key):
    lower = key.lower()
    return lower in ("token", "headers", "authorization") or lower.endswith("_token") or any(
        word in lower for word in ("api_key", "password", "secret"))


class MeasuredBackend(InferenceBackend):
    """Do not report a partial sum as the total when a call lacks usage."""

    def __init__(self, inner):
        self.inner = inner
        self.reset()

    def reset(self):
        self.calls = 0
        self.known = True
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.cost_usd = 0.0
        self.cost_known = True

    def generate(self, prompt, max_new_tokens, *, cancel_event=None):
        output = self.inner.generate(prompt, max_new_tokens, cancel_event=cancel_event)
        usage = self.inner.last_usage()
        self.calls += 1
        if usage is None:
            self.known = self.cost_known = False
        else:
            self.prompt_tokens += usage.prompt_tokens
            self.completion_tokens += usage.completion_tokens
            cost = estimate_cost(self.backend_kind(), self.model_name(), usage.prompt_tokens, usage.completion_tokens)
            if cost is None:
                self.cost_known = False
            else:
                self.cost_usd += cost
        return output

    def metrics(self):
        return {
            "prompt_tokens": self.prompt_tokens if self.known else None,
            "completion_tokens": self.completion_tokens if self.known else None,
            "cost_usd": self.cost_usd if self.cost_known else None,
        }

    def backend_kind(self):
        return self.inner.backend_kind()

    def model_name(self):
        return self.inner.model_name()

    def max_concurrency(self):
        return 1

    def close(self):
        self.inner.close()
