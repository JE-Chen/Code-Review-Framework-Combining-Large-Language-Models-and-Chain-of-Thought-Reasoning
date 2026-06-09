"""Secret-redaction patterns.

We test each pattern actually fires, that report counts are right, that
double-redaction is a no-op, and — most importantly — that ordinary
review-relevant code doesn't trigger false positives.
"""

from __future__ import annotations

import pytest

from prthinker.redaction import has_secrets, redact


# ----- positive cases (must redact) --------------------------------------

@pytest.mark.parametrize("secret,kind", [
    ("ghp_" + "a" * 36, "github-token"),
    ("gho_" + "a" * 30, "github-token"),
    ("sk-proj-" + "a" * 40, "openai-key"),
    ("sk-" + "x" * 40, "openai-key"),
    ("sk-ant-api03-" + "a" * 80, "anthropic-key"),
    ("sk_live_" + "a" * 24, "stripe-key"),
    ("rk_test_" + "a" * 30, "stripe-key"),
    ("AKIAIOSFODNN7EXAMPLE", "aws-access-key-id"),
    ("ASIAIOSFODNN7EXAMPLE", "aws-access-key-id"),
    ("xoxb-1234567890-12345-abcDEF123", "slack-token"),
    ("AIzaSy" + "A" * 33, "gcp-api-key"),
    ("AC" + "0" * 32, "twilio-sid"),
])
def test_known_secret_patterns_are_redacted(secret: str, kind: str) -> None:
    text = f"const KEY = '{secret}'"
    out, report = redact(text)
    assert secret not in out
    assert f"<REDACTED:{kind}>" in out
    assert report.counts.get(kind, 0) == 1
    assert bool(report) is True


def test_jwt_token_is_redacted() -> None:
    # Three base64url segments — header / payload / signature.
    jwt = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        ".eyJzdWIiOiIxIiwibmFtZSI6IkpvaG4ifQ"
        ".SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    )
    out, report = redact(f"Authorization: Bearer {jwt}")
    assert jwt not in out
    assert "<REDACTED:jwt>" in out
    assert report.counts["jwt"] == 1


def test_private_key_block_is_redacted_as_whole_block() -> None:
    text = (
        "header line\n"
        "-----BEGIN RSA PRIVATE KEY-----\n"
        "ABCDEF==\n"
        "GHIJKL==\n"
        "-----END RSA PRIVATE KEY-----\n"
        "footer line\n"
    )
    out, report = redact(text)
    assert "ABCDEF" not in out
    assert "GHIJKL" not in out
    assert "<REDACTED:private-key>" in out
    assert "header line" in out
    assert "footer line" in out
    assert report.counts["private-key"] == 1


def test_multiple_secrets_all_count() -> None:
    text = (
        "k1 = 'ghp_" + "a" * 36 + "'\n"
        "k2 = 'ghp_" + "b" * 36 + "'\n"
        "k3 = 'AKIAIOSFODNN7EXAMPLE'\n"
    )
    _, report = redact(text)
    assert report.counts["github-token"] == 2
    assert report.counts["aws-access-key-id"] == 1
    assert report.total == 3


def test_double_redaction_is_idempotent() -> None:
    text = "k = 'ghp_" + "a" * 36 + "'"
    once, _ = redact(text)
    twice, report2 = redact(once)
    assert once == twice
    # Second pass found no new secrets.
    assert report2.total == 0


# ----- report formatting --------------------------------------------------

def test_empty_report_has_clean_summary() -> None:
    _, report = redact("def foo():\n    return 42")
    assert bool(report) is False
    assert report.total == 0
    assert "no secrets redacted" in report.summary()


def test_report_summary_includes_kind_and_count() -> None:
    text = "k = 'ghp_" + "a" * 36 + "'"
    _, report = redact(text)
    summary = report.summary()
    assert "github-token" in summary
    assert "1×" in summary


# ----- negative cases (must NOT redact ordinary code) --------------------

def test_normal_python_code_does_not_redact() -> None:
    text = (
        "def hello():\n"
        "    name = 'world'\n"
        "    return f'hello {name}'\n"
        "\n"
        "if __name__ == '__main__':\n"
        "    print(hello())\n"
    )
    out, report = redact(text)
    assert out == text
    assert report.total == 0


def test_url_with_hex_path_does_not_redact() -> None:
    # Looks token-ish (long hex) but is a normal git SHA / CDN URL.
    text = (
        "url = 'https://cdn.example.com/static/"
        "abc123def456abc123def456abc123de.css'"
    )
    out, _ = redact(text)
    assert out == text


def test_uuid_does_not_redact() -> None:
    text = "id = '550e8400-e29b-41d4-a716-446655440000'"
    out, _ = redact(text)
    assert out == text


def test_has_secrets_short_circuits() -> None:
    assert has_secrets("nothing here") is False
    assert has_secrets("ghp_" + "a" * 36) is True
