"""Resolve only repository-grounded import links across supported languages."""

from pathlib import PurePosixPath

from prthinker.context_graph import LANGUAGE_BY_SUFFIX


def resolve_link(source: str, target: str, files: set[str]) -> str | None:
    stem = target.removeprefix("crate::").replace("::", "/")
    dotted = stem.replace(".", "/") if "/" not in stem and not stem.endswith((".h", ".hpp")) else stem
    candidates = [stem, str(PurePosixPath(source).parent / stem), dotted]
    matches = set()
    for candidate in candidates:
        for suffix in ("", *LANGUAGE_BY_SUFFIX.keys()):
            name = candidate + suffix
            if name in files and name != source:
                matches.add(name)
    return next(iter(matches)) if len(matches) == 1 else None


def language_for(path: str) -> str:
    return LANGUAGE_BY_SUFFIX.get(PurePosixPath(path).suffix.lower(), "")
