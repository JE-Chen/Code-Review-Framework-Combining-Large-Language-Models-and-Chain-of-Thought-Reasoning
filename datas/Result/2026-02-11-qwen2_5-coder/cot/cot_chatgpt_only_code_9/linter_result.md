```json
[
    {
        "rule_id": "global-variables",
        "severity": "warning",
        "message": "Global variables like SESSION, BASE_URL, and GLOBAL_CACHE can lead to unexpected behavior and make testing difficult.",
        "line": 4,
        "suggestion": "Consider using dependency injection or configuration objects."
    },
    {
        "rule_id": "magic-numbers",
        "severity": "warning",
        "message": "Magic numbers like 15 in the length check are hard to understand without context.",
        "line": 29,
        "suggestion": "Define a constant for this value, e.g., MAX_TITLE_LENGTH."
    },
    {
        "rule_id": "print-statements",
        "severity": "warning",
        "message": "Direct use of print statements for output is discouraged. Consider using logging instead.",
        "line": 38,
        "suggestion": "Use logging module for output."
    }
]
```