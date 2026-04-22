```json
[
    {
        "rule_id": "no-global-variables",
        "severity": "error",
        "message": "Global variables are used which can lead to unexpected behavior.",
        "line": 5,
        "suggestion": "Refactor to use local variables within functions."
    },
    {
        "rule_id": "duplicate-code",
        "severity": "warning",
        "message": "Duplicate code found in 'get_items' and 'complex_route'. Consider extracting common logic into a separate function.",
        "line": 29,
        "suggestion": "Extract common logic into a helper function."
    },
    {
        "rule_id": "input-validation",
        "severity": "error",
        "message": "Input validation missing for 'param' in 'complex_route'.",
        "line": 38,
        "suggestion": "Validate 'param' before processing."
    },
    {
        "rule_id": "magic-numbers",
        "severity": "warning",
        "message": "Magic numbers found in 'complex_route'. Consider using named constants.",
        "line": 42,
        "suggestion": "Define constants for magic numbers."
    },
    {
        "rule_id": "missing-documentation",
        "severity": "warning",
        "message": "Missing docstring for 'index' route handler.",
        "line": 14,
        "suggestion": "Add a docstring describing the endpoint."
    },
    {
        "rule_id": "missing-documentation",
        "severity": "warning",
        "message": "Missing docstring for 'add_item' route handler.",
        "line": 18,
        "suggestion": "Add a docstring describing the endpoint."
    }
]
```