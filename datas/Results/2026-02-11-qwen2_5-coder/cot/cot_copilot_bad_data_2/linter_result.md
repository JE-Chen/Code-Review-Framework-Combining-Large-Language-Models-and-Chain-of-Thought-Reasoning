```json
[
    {
        "rule_id": "io-in-function",
        "severity": "error",
        "message": "I/O operations should be avoided within functions.",
        "line": 2,
        "suggestion": "Refactor the function to separate I/O logic."
    },
    {
        "rule_id": "io-in-function",
        "severity": "error",
        "message": "I/O operations should be avoided within functions.",
        "line": 9,
        "suggestion": "Refactor the function to separate I/O logic."
    },
    {
        "rule_id": "io-in-function",
        "severity": "error",
        "message": "I/O operations should be avoided within functions.",
        "line": 21,
        "suggestion": "Refactor the function to separate I/O logic."
    },
    {
        "rule_id": "io-in-function",
        "severity": "error",
        "message": "I/O operations should be avoided within functions.",
        "line": 29,
        "suggestion": "Refactor the function to separate I/O logic."
    },
    {
        "rule_id": "hidden-flags",
        "severity": "warning",
        "message": "The use of a hidden flag 'hidden_flag' makes the function's behavior unpredictable.",
        "line": 5,
        "suggestion": "Pass the flag as an explicit parameter."
    },
    {
        "rule_id": "mutable-default-args",
        "severity": "error",
        "message": "Mutable default arguments are not allowed.",
        "line": 23,
        "suggestion": "Replace with a non-mutable default or use None and initialize inside the function."
    },
    {
        "rule_id": "shared-state",
        "severity": "warning",
        "message": "The use of a global dictionary 'global_config' can lead to unexpected behavior.",
        "line": 26,
        "suggestion": "Pass the configuration as an argument to avoid global state."
    },
    {
        "rule_id": "unsafe-eval",
        "severity": "error",
        "message": "Using eval can introduce security vulnerabilities.",
        "line": 33,
        "suggestion": "Validate and sanitize user input before evaluating."
    }
]
```