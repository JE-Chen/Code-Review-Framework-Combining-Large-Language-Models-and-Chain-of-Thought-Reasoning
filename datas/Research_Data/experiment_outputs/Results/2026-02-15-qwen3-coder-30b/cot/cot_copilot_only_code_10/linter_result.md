```json
[
  {
    "rule_id": "no-global-variables",
    "severity": "warning",
    "message": "Usage of global variable 'GLOBAL_CACHE' reduces modularity and testability.",
    "line": 8,
    "suggestion": "Pass cache as a parameter or use dependency injection."
  },
  {
    "rule_id": "no-duplicate-code",
    "severity": "warning",
    "message": "Functions 'get_users', 'get_posts', and 'get_todos' have duplicated logic.",
    "line": 19,
    "suggestion": "Refactor into a single generic method that accepts an endpoint."
  },
  {
    "rule_id": "no-implicit-exception-handling",
    "severity": "error",
    "message": "Catching generic Exception hides potential programming errors.",
    "line": 13,
    "suggestion": "Catch specific exceptions like requests.RequestException."
  },
  {
    "rule_id": "no-uncontrolled-resource-usage",
    "severity": "warning",
    "message": "Global session object may cause resource leaks in long-running applications.",
    "line": 3,
    "suggestion": "Use context managers or ensure proper cleanup of sessions."
  },
  {
    "rule_id": "no-hardcoded-values",
    "severity": "warning",
    "message": "Hardcoded URL path '/users', '/posts', '/todos' reduces flexibility.",
    "line": 19,
    "suggestion": "Move endpoints to a configuration or constants module."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic numbers '5' and '20' used in conditional checks without explanation.",
    "line": 44,
    "suggestion": "Define named constants for these thresholds."
  },
  {
    "rule_id": "no-bad-comments",
    "severity": "info",
    "message": "Comments are missing in some functions for clarity.",
    "line": 19,
    "suggestion": "Add docstrings or inline comments explaining behavior."
  }
]
```