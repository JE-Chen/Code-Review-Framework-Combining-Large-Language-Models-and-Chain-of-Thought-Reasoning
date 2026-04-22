```json
[
    {
        "rule_id": "default-mutable-arg",
        "severity": "error",
        "message": "Mutable default argument 'container' used.",
        "line": 2,
        "suggestion": "Use None as the default value and initialize inside the function."
    },
    {
        "rule_id": "shared-state",
        "severity": "error",
        "message": "Shared mutable state used in 'append_global'.",
        "line": 6,
        "suggestion": "Pass the list explicitly or encapsulate it in a class."
    },
    {
        "rule_id": "mutation-of-input",
        "severity": "error",
        "message": "Input argument 'data' is mutated.",
        "line": 10,
        "suggestion": "Create a copy of the input if mutation is not expected."
    },
    {
        "rule_id": "inconsistent-return-types",
        "severity": "error",
        "message": "Function returns different types based on 'flag'.",
        "line": 18,
        "suggestion": "Return a consistent type or handle all cases explicitly."
    },
    {
        "rule_id": "unnecessary-work-in-loop",
        "severity": "warning",
        "message": "Repeating 'len(values)' calculation inside loop.",
        "line": 26,
        "suggestion": "Cache the length outside the loop."
    },
    {
        "rule_id": "risky-eval",
        "severity": "error",
        "message": "Using eval to execute code string.",
        "line": 35,
        "suggestion": "Replace eval with a safer alternative or avoid dynamic code execution."
    }
]
```