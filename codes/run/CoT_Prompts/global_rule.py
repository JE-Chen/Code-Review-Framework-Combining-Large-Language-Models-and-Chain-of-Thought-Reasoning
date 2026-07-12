GLOBAL_RULE_TEMPLATE = """
Please conduct a code review according to the following global rules:

1. Readability & Consistency
   - Check indentation, formatting, and comments for clarity.
   - Ensure code style follows team conventions (naming rules, formatting tools).

2. Naming Conventions
   - Variable, function, and class names must be descriptive and meaningful.
   - Maintain semantic clarity and consistency across the codebase.

3. Software Engineering Standards
   - Code should be modular, maintainable, and testable.
   - Avoid duplicate code; encourage refactoring and abstraction.

4. Logic & Correctness
   - Verify correctness of program logic and identify potential bugs.
   - Check boundary conditions and exception handling.
   - A diff shows only changed and nearby lines; imports, functions, and
     variables defined elsewhere in the file are still present. Do not treat
     something as undefined, not imported, or missing just because its
     definition is not in the shown lines.
   - Raise a concern only when the visible code supports it; avoid speculative
     "could/might/may be a problem if ..." remarks with no concrete trigger.

5. Performance & Security
   - Assess for unnecessary performance bottlenecks.
   - Review for security risks (e.g., input validation, resource management).

6. Documentation & Testing
   - Ensure necessary comments and documentation are present.
   - Verify sufficient unit and integration tests are included.

7. Scoring & Feedback Style
   - Balance conciseness with comprehensiveness.
   - Do not penalize completeness for being less concise.

{rag_rules_section}
---

# Prompt Content
{prompt}
"""

def build_global_rule_template(rag_rules=None, prompt=""):
    if not rag_rules:
        rag_rules_section = ""  # 忽略 RAG Rules 區塊
    else:
        if isinstance(rag_rules, list):
            rag_rules_text = "".join(f"   - {rule}" for rule in rag_rules)
        else:
            rag_rules_text = f"   - {rag_rules}"

        rag_rules_section = f"""
8. RAG Rules (Retrieval-Augmented Guidance)
   - Apply RAG-provided rules when available.
   - If a rule conflicts or duplicates existing global rules, prioritize the RAG rule.
   - Ensure integration of RAG rules maintains consistency with overall review standards.
{rag_rules_text}
"""

    return GLOBAL_RULE_TEMPLATE.format(
        rag_rules_section=rag_rules_section,
        prompt=prompt
    )
