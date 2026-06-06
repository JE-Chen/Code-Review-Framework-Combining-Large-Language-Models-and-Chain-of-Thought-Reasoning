"""RemoteBackendConfig URL scheme normalization.

The CI passes PRTHINKER_REMOTE_URL straight from a repo secret. When that
value lacks a scheme (``host:9000``) httpx fails deep in its transport with
"Request URL is missing an 'http://' or 'https://' protocol". The config
normalises the URL at the boundary: a bare host gets ``https://`` (the
HTTPS-only default), an explicit http/https is respected, and any other
scheme is rejected with a clear error.
"""

from __future__ import annotations

import pytest

from prthinker.config import RemoteBackendConfig, _normalize_remote_url


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("host", "https://host"),
        ("host:9000", "https://host:9000"),
        ("kvgh-gpu.example.com/", "https://kvgh-gpu.example.com/"),
        ("  host:9000  ", "https://host:9000"),  # surrounding whitespace stripped
        ("https://host", "https://host"),  # explicit https respected
        ("http://1.2.3.4:9000", "http://1.2.3.4:9000"),  # explicit http (no-TLS tunnel)
        ("HTTPS://Host", "HTTPS://Host"),  # scheme detected case-insensitively
    ],
)
def test_normalize_remote_url(raw, expected):
    assert _normalize_remote_url(raw) == expected


@pytest.mark.parametrize("bad", ["", "   ", None])
def test_empty_url_rejected(bad):
    with pytest.raises(ValueError, match="url is required"):
        _normalize_remote_url(bad)


@pytest.mark.parametrize("bad", ["ftp://host", "file:///etc/passwd", "ws://host"])
def test_non_http_scheme_rejected(bad):
    with pytest.raises(ValueError, match="scheme must be http or https"):
        _normalize_remote_url(bad)


def test_config_applies_normalization():
    cfg = RemoteBackendConfig(url="host:9000")
    assert cfg.url == "https://host:9000"


def test_config_preserves_explicit_scheme():
    cfg = RemoteBackendConfig(url="http://localhost:9000")
    assert cfg.url == "http://localhost:9000"


def test_config_rejects_empty_url():
    with pytest.raises(ValueError, match="url is required"):
        RemoteBackendConfig(url="")
