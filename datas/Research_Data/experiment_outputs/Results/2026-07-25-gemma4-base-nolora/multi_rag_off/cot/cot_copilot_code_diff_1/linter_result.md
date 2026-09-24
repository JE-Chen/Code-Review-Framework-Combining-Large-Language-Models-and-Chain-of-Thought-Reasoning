```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 'meanVal' uses camelCase, which is inconsistent with the snake_case convention typically used in Python (PEP 8).",
    "line": 28,
    "suggestion": "Rename 'meanVal' to 'mean_val'."
  },
  {
    "rule_id": "duplicate-code",
    "severity": "info",
    "message": "Redundant call to 'statistics.mean(DATA)'. The value is already stored in 'meanVal'.",
    "line": 30,
    "suggestion": "Use 'RESULTS[\"meanAgain\"] = meanVal'."
  },
  {
    "rule_id": "duplicate-code",
    "severity": "info",
    "message": "Redundant call to 'statistics.median(DATA)'. The value is calculated twice in the same block.",
    "line": 37,
    "suggestion": "Store 'statistics.median(DATA)' in a variable and reuse it for 'medianPlus42'."
  },
  {
    "rule_id": "software-engineering-standard",
    "severity": "warning",
    "message": "Use of 'global' variables ('DATA', 'RESULTS') makes the application stateful and not thread-safe, which will cause issues in a production WSGI environment.",
    "line": 21,
    "suggestion": "Use a database or a caching layer (like Redis) to manage state."
  }
]
```