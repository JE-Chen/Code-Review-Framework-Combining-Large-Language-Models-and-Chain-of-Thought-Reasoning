"""Infrastructure-as-code review mode (self-registering).

A focused whole-diff pass that frames the model as an IaC reviewer:
Terraform, Kubernetes manifests, Dockerfiles, and GitHub Actions
workflows. The model is told to consider only the supplied unified diff
and to emit findings as a strict JSON array.

Per ``paper_rule.md`` no-fabrication: this module ships only the prompt
template; no quality claim is made about its findings.
"""

from __future__ import annotations

from prthinker.review_modes import register_mode

_SEVERITY_VALUES = "info / warning / error"
_EMPTY_ARRAY = "[]"

_FOCUS_CHECKLIST = (
    "- Terraform: over-broad IAM policies (wildcard actions / principals), "
    "public S3 / GCS / blob buckets, unrestricted security-group ingress.\n"
    "- Kubernetes: missing CPU / memory resource limits, privileged "
    "containers, hostPath mounts, containers running as root.\n"
    "- Dockerfile: :latest base-image tags, running as root, secret "
    "leakage baked into layers.\n"
    "- GitHub Actions: unpinned actions (tag / branch instead of a commit "
    "SHA), secret leakage via echo / logs, over-broad workflow "
    "permissions."
)


def _build_iac_prompt(diff_text: str) -> str:
    """Assemble the IaC review prompt body around ``diff_text``."""
    return (
        "You are performing a focused infrastructure-as-code (IaC) review "
        "pass on a pull request. Consider ONLY the supplied unified diff "
        "below; do not assume context outside it.\n\n"
        "Look specifically for IaC misconfiguration across Terraform, "
        "Kubernetes, Dockerfile, and GitHub Actions:\n"
        f"{_FOCUS_CHECKLIST}\n\n"
        "Report your findings as a JSON array of objects, each with at "
        "least these keys: \"path\" (string), \"line\" (integer), "
        f"\"severity\" (one of {_SEVERITY_VALUES}), and \"comment\" "
        "(string). If nothing in the focus list applies, return an empty "
        f"array {_EMPTY_ARRAY}.\n\n"
        "Unified diff:\n"
        f"{diff_text}"
    )


@register_mode("iac", "Infrastructure-as-code pass")
def build_prompt(diff_text: str) -> str:
    """Build the iac review prompt for a unified diff."""
    return _build_iac_prompt(diff_text)


__all__ = ["build_prompt"]
