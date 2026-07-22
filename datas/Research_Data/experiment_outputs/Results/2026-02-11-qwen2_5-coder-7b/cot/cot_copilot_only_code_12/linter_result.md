```json
[
    {
        "rule_id": "no-unused-vars",
        "severity": "warning",
        "message": "The variable 'tempStorage' is assigned but never used.",
        "line": 9,
        "suggestion": "Remove the unused variable or use it within the code."
    },
    {
        "rule_id": "inconsistent-naming",
        "severity": "warning",
        "message": "Variable names should follow lowercase_with_underscores convention.",
        "line": 9,
        "suggestion": "Rename 'tempStorage' to something like 'temporary_storage'."
    },
    {
        "rule_id": "duplicate-code",
        "severity": "warning",
        "message": "Duplicate code detected in calcStats function for columns 'A' and 'B'.",
        "line": 18,
        "suggestion": "Refactor into a separate function that takes column name as an argument."
    },
    {
        "rule_id": "missing-docstrings",
        "severity": "info",
        "message": "Function 'loadData' lacks a docstring describing its purpose and parameters.",
        "line": 12,
        "suggestion": "Add a docstring explaining what the function does."
    },
    {
        "rule_id": "missing-docstrings",
        "severity": "info",
        "message": "Function 'calcStats' lacks a docstring describing its purpose and parameters.",
        "line": 23,
        "suggestion": "Add a docstring explaining what the function does."
    },
    {
        "rule_id": "missing-docstrings",
        "severity": "info",
        "message": "Function 'plotData' lacks a docstring describing its purpose and parameters.",
        "line": 33,
        "suggestion": "Add a docstring explaining what the function does."
    }
]
```