```json
[
    {
        "rule_id": "global-state-mutation",
        "severity": "warning",
        "message": "Using global state directly can lead to unpredictable behavior.",
        "line": 1,
        "suggestion": "Consider using a class or context manager to encapsulate the state."
    },
    {
        "rule_id": "function-length",
        "severity": "warning",
        "message": "Function 'process_items' has too many lines and complex logic.",
        "line": 18,
        "suggestion": "Refactor into smaller functions for better readability and testability."
    }
]
```