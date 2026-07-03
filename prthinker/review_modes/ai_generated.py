from prthinker.review_modes._registry import register_mode


@register_mode("ai-generated", "AI-generated code reliability review")
def build_prompt(diff_text: str) -> str:
    return (
        "Review this potentially AI-generated change for hallucinated packages/APIs, duplication, unnecessary abstraction, test overfitting, insecure defaults, and missing provenance. Return a JSON finding array with path, line, severity, comment.\n\n"
        + diff_text
    )
