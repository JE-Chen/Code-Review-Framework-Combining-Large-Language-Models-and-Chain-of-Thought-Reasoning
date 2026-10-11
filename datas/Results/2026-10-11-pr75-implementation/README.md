# Offline implementation validation

This archive contains test, parser, installation, documentation and editor integration checks. It is not a model experiment or a thesis result.

Reproduce the runner checks with `python scripts/verify_implementation.py NEW_OUTPUT --minimum-python PYTHON310`; run `scripts/probe_polyglot.py` with the optional grammar dependency installed. Editor commands are recorded in editor-verification/*.json. All contract service probes used closed local ports. No benchmark or ablation model generations were run.

The latest runner checks are implementation-final/. Earlier checks and the two files before the UTF-8 protocol fix are retained for traceability. Source hashes normalize CRLF to LF; raw evidence bytes are preserved by Git attributes.
