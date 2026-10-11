"""Generation limits remain auditable while credentials and unknown usage do not."""

from prthinker.benchmark_measurement import MeasuredBackend, public_configuration
from tests.conftest import FakeBackend


def test_configuration_keeps_generation_controls_and_drops_secrets():
    config = public_configuration({"max_new_tokens": 8192, "api_key": "private",
                                  "github_token": "private", "url": "https://user:pass@host/path?key=private"})
    assert config == {"max_new_tokens": 8192, "url": "https://host/path"}


def test_unreported_tokens_remain_unknown():
    backend = MeasuredBackend(FakeBackend(["ok"]))
    backend.generate("prompt", 32)
    assert backend.metrics() == {"prompt_tokens": None, "completion_tokens": None, "cost_usd": None}
    backend.reset()
    assert backend.calls == 0
