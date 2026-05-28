# Adversarial seed corpus

`seed.jsonl` is a **small, hand-authored seed** illustrating each of
the four `AttackCategory` values defined in `reviewmind.adversarial`.

It is **not** a benchmark. Specifically:

- It does not claim coverage of the adversarial input space.
- It does not ship measured detection-rate numbers for any backend.
- It is intended as a starting point for users to extend with their
  own attack cases, run `reviewmind adversarial-eval` against their
  chosen backends, and produce their own dataset of outcomes.

Per the project's `paper_rule.md` (no-fabrication HARD rule), any
robustness claim in a paper must come from the user's own run of
`adversarial-eval`, with the raw outcome rows backing each number.
The framework records every outcome into a SQLite table for that
purpose; it does not include pre-computed scores.

## Extending the corpus

Append one JSON object per line. Required fields:

| key | type | meaning |
|---|---|---|
| `id` | string | stable identifier for cross-run comparison |
| `category` | string | one of `direct_injection`, `encoded_payload`, `split_injection`, `role_hijack` |
| `diff_text` | string | the unified diff to feed the reviewer |
| `expected_behavior` | string | `flag` / `ignore` / `neither` |
| `success_markers` | list[string] | substrings in model output that mean the attack succeeded |
| `detection_markers` | list[string] | substrings that mean the reviewer recognized the attack |
| `notes` | string | optional human-readable rationale |

Markers are matched case-insensitively. See
`reviewmind/adversarial.py:detect_bypass` for the exact decision logic.
