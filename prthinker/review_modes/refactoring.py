from prthinker.review_modes._registry import register_mode


@register_mode("refactoring", "Behavior-preserving refactoring review")
def build_prompt(diff_text: str) -> str:
    return (
        "Review whether this refactoring preserves behavior, public APIs, "
        "error semantics, concurrency, and performance. Return a JSON "
        "finding array with path, line, severity, comment. Do not report "
        "style-only changes.\n\n"
        + diff_text
    )
