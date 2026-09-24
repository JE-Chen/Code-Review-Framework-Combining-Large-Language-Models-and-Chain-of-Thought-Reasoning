```json
[
    {
        "rule_id": "global-variables",
        "severity": "error",
        "message": "Using global variables can lead to unexpected behavior and difficulties in testing.",
        "line": 9,
        "suggestion": "Pass global variables as parameters to functions."
    },
    {
        "rule_id": "mutable-default-arguments",
        "severity": "error",
        "message": "Mutable default arguments like lists and dictionaries can lead to unexpected behavior.",
        "line": 14,
        "suggestion": "Initialize mutable defaults within the function body."
    },
    {
        "rule_id": "unhandled-exceptions",
        "severity": "error",
        "message": "Exception handling without specific exceptions can hide bugs.",
        "line": 23,
        "suggestion": "Catch specific exceptions or re-raise them with context."
    },
    {
        "rule_id": "unnecessary-complexity",
        "severity": "warning",
        "message": "The function does too many things and lacks clarity.",
        "line": 13,
        "suggestion": "Split the function into smaller, more focused functions."
    },
    {
        "rule_id": "inefficient-calculation",
        "severity": "warning",
        "message": "Repeating calculations inside loops can impact performance.",
        "line": 26,
        "suggestion": "Cache results of expensive calculations."
    },
    {
        "rule_id": "redundant-code",
        "severity": "warning",
        "message": "The same code appears multiple times.",
        "line": 36,
        "suggestion": "Refactor out repeated logic into a separate function."
    },
    {
        "rule_id": "inconsistent-return-types",
        "severity": "error",
        "message": "The function returns different types based on conditions.",
        "line": 47,
        "suggestion": "Ensure consistent return types."
    },
    {
        "rule_id": "unnecessary-imports",
        "severity": "info",
        "message": "Some imports are not used in the code.",
        "line": 4,
        "suggestion": "Remove unused imports."
    }
]
```