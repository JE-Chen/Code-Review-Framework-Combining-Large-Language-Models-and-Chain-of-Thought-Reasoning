```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 'meanVal' uses camelCase, which is inconsistent with PEP 8 snake_case convention for variables.",
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
    "message": "Redundant call to 'statistics.median(DATA)'.",
    "line": 37,
    "suggestion": "Store the result of 'statistics.median(DATA)' in a variable and reuse it for 'medianPlus42'."
  },
  {
    "rule_id": "software-engineering-standard",
    "severity": "warning",
    "message": "Use of 'global' variables ('DATA', 'RESULTS') makes the application stateful and not thread-safe, which is problematic for Flask deployments.",
    "line": 20,
    "suggestion": "Use a database or a caching layer (like Redis) to manage state."
  }
]
```