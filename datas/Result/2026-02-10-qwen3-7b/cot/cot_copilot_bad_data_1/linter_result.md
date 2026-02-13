```python
[
    {
        "rule_id": "use-secure-operations",
        "severity": "error",
        "message": "The `run_code` function uses `eval` which is insecure and not justified.",
        "line": 18,
        "suggestion": "Avoid using `eval` for dynamic code execution. Use explicit logic or safe parsing instead."
    }
]
```