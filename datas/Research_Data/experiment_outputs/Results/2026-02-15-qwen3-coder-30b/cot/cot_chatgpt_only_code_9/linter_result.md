```json
[
  {
    "rule_id": "no-global-state",
    "severity": "warning",
    "message": "Usage of global state (GLOBAL_CACHE) reduces testability and modularity.",
    "line": 10,
    "suggestion": "Pass cache as a parameter or use dependency injection."
  },
  {
    "rule_id": "no-raw-exceptions",
    "severity": "warning",
    "message": "Catching generic Exception hides specific error types and makes debugging harder.",
    "line": 18,
    "suggestion": "Catch specific exceptions like requests.RequestException or ValueError."
  },
  {
    "rule_id": "no-duplicated-logic",
    "severity": "warning",
    "message": "Repeated fetch logic in get_users, get_posts, and get_todos can be abstracted into a single reusable function.",
    "line": 23,
    "suggestion": "Refactor repeated patterns into a shared method."
  },
  {
    "rule_id": "no-hardcoded-values",
    "severity": "warning",
    "message": "Hardcoded string 'Special User' and similar messages reduce maintainability.",
    "line": 39,
    "suggestion": "Move such strings to constants or configuration."
  },
  {
    "rule_id": "no-unvalidated-input",
    "severity": "warning",
    "message": "Direct use of JSON data without validation may cause runtime errors.",
    "line": 34,
    "suggestion": "Validate structure and types before accessing nested fields."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic numbers 5 and 20 used in conditional checks make intent unclear.",
    "line": 47,
    "suggestion": "Use named constants instead of magic numbers."
  }
]
```