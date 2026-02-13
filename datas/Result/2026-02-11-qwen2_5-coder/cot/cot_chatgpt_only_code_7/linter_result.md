```json
[
    {
        "rule_id": "no-magic-numbers",
        "severity": "warning",
        "message": "Magic numbers (0.3, 0.2) should be replaced with named constants.",
        "line": 89,
        "suggestion": "Define constants at the beginning of the file."
    },
    {
        "rule_id": "no-sleep-in-main-thread",
        "severity": "error",
        "message": "Using 'time.sleep' in the main thread can block the UI.",
        "line": 89,
        "suggestion": "Use a separate thread or timer for blocking operations."
    },
    {
        "rule_id": "no-sleep-in-main-thread",
        "severity": "error",
        "message": "Using 'time.sleep' in the main thread can block the UI.",
        "line": 102,
        "suggestion": "Use a separate thread or timer for blocking operations."
    }
]
```