"""Review preset expansion for the CLI.

Presets are thin bundles over existing flags. They do not introduce a new
review path; they only turn on the checks and focused modes a caller would
otherwise spell out by hand.
"""

from __future__ import annotations

import argparse


_PRESET_MODES: dict[str, tuple[str, ...]] = {
    "backend": ("security", "performance", "test-coverage"),
    "frontend": ("accessibility", "performance", "pii", "test-coverage"),
    "security": ("security", "secret-scan", "pii"),
    "release": ("security", "test-coverage"),
}


def _merge_csv(existing: str, additions: tuple[str, ...]) -> str:
    values = [item.strip() for item in existing.split(",") if item.strip()]
    seen = set(values)
    for addition in additions:
        if addition not in seen:
            values.append(addition)
            seen.add(addition)
    return ",".join(values)


def apply_review_preset(args: argparse.Namespace) -> None:
    """Expand ``--review-preset`` into ordinary argparse attributes in place."""
    preset = (getattr(args, "review_preset", "none") or "none").strip()
    if preset == "none":
        return
    args.review_modes = _merge_csv(
        getattr(args, "review_modes", "") or "", _PRESET_MODES.get(preset, ())
    )
    if preset in {"backend", "release"}:
        args.api_consistency = True
        args.dep_upgrade_check = True
    if preset in {"release"}:
        args.diff_entropy = True
        args.reproducibility_check = True
        args.judge = True
    if preset == "security":
        args.redact_secrets = True
        if getattr(args, "gate_on", "none") == "none":
            args.gate_on = "warning"


__all__ = ["apply_review_preset"]
