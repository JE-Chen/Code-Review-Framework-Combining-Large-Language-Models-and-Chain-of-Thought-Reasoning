[
    {
        "rule_id": "global-variable-usage",
        "severity": "error",
        "message": "Global variable `GLOBAL_THING` is not used in the function and should be encapsulated.",
        "line": 10,
        "suggestion": "Encapsulate global state in a class or module for better maintainability."
    },
    {
        "rule_id": "function-name-unclear",
        "severity": "error",
        "message": "Function `do_everything_and_nothing_at_once` is too vague and lacks clarity.",
        "line": 1,
        "suggestion": "Rename to something like `process_data` or `generate_and_analyze` for better intent."
    },
    {
        "rule_id": "variable-naming-inefficient",
        "severity": "error",
        "message": "Variable `data_container` is overly generic and could be more descriptive.",
        "line": 17,
        "suggestion": "Use `processed_values` or `generated_values` for clarity."
    },
    {
        "rule_id": "missing-exception-handling",
        "severity": "error",
        "message": "Missing explicit handling of exceptions in critical paths.",
        "line": 22,
        "suggestion": "Add try-except blocks around critical operations for robustness."
    },
    {
        "rule_id": "inconsistent-logic",
        "severity": "error",
        "message": "Conditional logic in `do_everything_and_nothing_at_once` is hard to follow.",
        "line": 24,
        "suggestion": "Split into smaller helper functions for readability and maintainability."
    },
    {
        "rule_id": "performance-bottlenecks",
        "severity": "error",
        "message": "Repeated random() and math.sqrt() calls in loops are inefficient.",
        "line": 20,
        "suggestion": "Cache results or precompute values outside loops for performance."
    },
    {
        "rule_id": "missing-docstrings",
        "severity": "error",
        "message": "No docstrings for public functions or complex logic blocks.",
        "line": 1,
        "suggestion": "Add docstrings explaining function purpose and parameters."
    },
    {
        "rule_id": "unused-variables",
        "severity": "error",
        "message": "Unused variables like `weird_sum` and `temp` are not explained.",
        "line": 32,
        "suggestion": "Remove or document unused variables for clarity."
    },
    {
        "rule_id": "side-effect-calls",
        "severity": "error",
        "message": "`df.sample()` and `STRANGE_CACHE` modifications are not documented.",
        "line": 38,
        "suggestion": "Document side effects and encapsulate mutable state."
    },
    {
        "rule_id": "overly-complex-logic",
        "severity": "error",
        "message": "Logic in `do_everything_and_nothing_at_once` is too intertwined.",
        "line": 40,
        "suggestion": "Break into smaller functions with clear responsibilities."
    }
]