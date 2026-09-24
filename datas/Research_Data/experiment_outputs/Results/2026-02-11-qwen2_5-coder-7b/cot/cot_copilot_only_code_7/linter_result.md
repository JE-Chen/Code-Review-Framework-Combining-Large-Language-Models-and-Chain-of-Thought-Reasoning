```json
[
    {
        "rule_id": "global-variables",
        "severity": "error",
        "message": "Global variables are used, which can lead to unexpected behavior and make the code harder to maintain.",
        "line": 3,
        "suggestion": "Refactor to use instance variables or pass data through methods."
    },
    {
        "rule_id": "hardcoded-values",
        "severity": "warning",
        "message": "Hardcoded values like 'default' in GLOBAL_MODE are used, which makes it difficult to change without modifying multiple places.",
        "line": 8,
        "suggestion": "Use constants or enums for hardcoded values."
    },
    {
        "rule_id": "string-concatenation",
        "severity": "warning",
        "message": "String concatenation in handle_btn1 can become inefficient with many additions.",
        "line": 20,
        "suggestion": "Consider using a list to collect strings and join them once."
    },
    {
        "rule_id": "magic-numbers",
        "severity": "warning",
        "message": "Magic number 5 is used in handle_btn2, which lacks context.",
        "line": 29,
        "suggestion": "Define a constant or variable for this value."
    }
]
```