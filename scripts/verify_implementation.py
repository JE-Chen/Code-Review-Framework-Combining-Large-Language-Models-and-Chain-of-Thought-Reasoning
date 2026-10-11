"""Archive offline checks and wheel installation without model experiments."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import subprocess
import sys
import tarfile
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(command, cwd, log):
    """Run a bounded argument list and persist the complete output."""
    with log.open("wb") as handle:
        result = subprocess.run(command, cwd=cwd, stdout=handle,
                                stderr=subprocess.STDOUT, timeout=900, check=False)
    return {"command": command, "exit_code": result.returncode,
            "log": log.name, "sha256": hashlib.sha256(log.read_bytes()).hexdigest()}


def lint_counts(python, directory):
    packages = [name for name in ("prthinker", "tests", "scripts") if (directory / name).is_dir()]
    result = subprocess.run([python, "-m", "ruff", "check", *packages,
                             "--output-format", "json"], cwd=directory, capture_output=True,
                            timeout=120, check=False)
    rows = json.loads(result.stdout)
    return Counter((Path(row["filename"]).relative_to(directory).as_posix(),
                    row["code"], row["message"]) for row in rows)


def lint_delta(python, log):
    """Compare violation identities, unaffected by shifted line numbers."""
    with tempfile.TemporaryDirectory(prefix="prthinker-lint-") as temporary:
        baseline = Path(temporary)
        archive = subprocess.run(["git", "archive", "HEAD", "pyproject.toml", "prthinker", "tests", "codes"],
                                 cwd=ROOT, capture_output=True, timeout=60, check=True).stdout
        with tarfile.open(fileobj=io.BytesIO(archive)) as handle:
            for member in handle.getmembers():
                target = baseline / member.name
                if not target.resolve().is_relative_to(baseline.resolve()):
                    raise ValueError("archive escapes baseline directory")
                if member.isfile():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    source = handle.extractfile(member)
                    if source:
                        with source:
                            target.write_bytes(source.read())
        before, after = lint_counts(python, baseline), lint_counts(python, ROOT)
    new = after - before
    payload = {"baseline_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
               "baseline_violations": sum(before.values()), "current_violations": sum(after.values()),
               "new_violations": [{"file": key[0], "code": key[1], "message": key[2], "count": count}
                                  for key, count in new.items()]}
    log.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return {"command": [python, "-m", "ruff", "check", "prthinker", "tests", "scripts"],
            "exit_code": 1 if new else 0, "log": log.name,
            "sha256": hashlib.sha256(log.read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--minimum-python", required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    python = sys.executable
    checks = []
    commands = [
        ("pytest-current", [python, "-m", "pytest", "-q"]),
        ("pytest-minimum", [str(Path(args.minimum_python).resolve()), "-m", "pytest", "-q"]),
        ("bandit", [python, "-m", "bandit", "-c", "pyproject.toml", "-r", "prthinker", "-q"]),
        ("documentation", [python, "-m", "sphinx", "-b", "html", "-q", "docs", "docs/_build/html"]),
        ("build", [python, "-m", "build"]),
    ]
    for name, command in commands:
        check = run(command, ROOT, output / (name + ".log"))
        checks.append(check)
        print(name, check["exit_code"], flush=True)
    checks.append(lint_delta(python, output / "ruff-delta.json"))
    distributions = sorted((ROOT / "dist").glob("prthinker-0.1.0*"))
    checks.append(run([python, "-m", "twine", "check", *map(str, distributions)], ROOT, output / "twine.log"))
    with tempfile.TemporaryDirectory(prefix="prthinker-install-") as temporary:
        environment = Path(temporary) / "venv"
        checks.append(run([args.minimum_python, "-m", "venv", str(environment)], ROOT, output / "venv.log"))
        installed = environment / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
        wheel = next(path for path in distributions if path.suffix == ".whl")
        checks.append(run([str(installed), "-m", "pip", "install", str(wheel) + "[runner]"], ROOT, output / "install.log"))
        for command in ([], ["ide"], ["pr-summary"], ["ablation-study"], ["quality"], ["release-check"]):
            name = command[0] if command else "root"
            checks.append(run([str(installed), "-m", "prthinker", *command, "--help"], temporary,
                              output / ("smoke-" + name + ".log")))
        checks.append(run([str(installed), "-c",
                           ("from importlib.resources import files; "
                           "p=files('prthinker').joinpath('adversarial_corpus/v1.jsonl'); "
                           "assert len(p.read_text(encoding='utf-8').splitlines()) == 24")], temporary,
                          output / "smoke-corpus.log"))
    payload = {"schema_version": 1, "measurement": "offline_implementation_validation",
               "status": "passed" if all(check["exit_code"] == 0 for check in checks) else "failed",
               "checks": checks,
               "distributions": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in distributions}}
    (output / "checks.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(payload["status"], flush=True)
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
