```json
[
  {
    "rule_id": "no-global-mutable-state",
    "severity": "error",
    "message": "Use of global mutable state (USERS, REQUEST_LOG, LAST_RESULT) makes the application non-deterministic and hard to test.",
    "line": 6,
    "suggestion": "Move state into a class or use dependency injection for better testability."
  },
  {
    "rule_id": "no-implicit-any",
    "severity": "warning",
    "message": "Missing type annotations make code harder to understand and maintain.",
    "line": 12,
    "suggestion": "Add type hints to function parameters and return values."
  },
  {
    "rule_id": "no-unvalidated-input",
    "severity": "error",
    "message": "Direct access to request.json without validation can lead to runtime errors.",
    "line": 17,
    "suggestion": "Validate input data using schema validation like Pydantic or marshmallow."
  },
  {
    "rule_id": "no-bad-exception-handling",
    "severity": "warning",
    "message": "No exception handling for integer conversion when filtering users by age.",
    "line": 40,
    "suggestion": "Wrap int() conversion in try-except block to handle invalid input gracefully."
  },
  {
    "rule_id": "no-duplicated-code",
    "severity": "warning",
    "message": "Repeated logic in PUT and DELETE handlers could be abstracted.",
    "line": 38,
    "suggestion": "Extract common user lookup logic into a reusable helper function."
  },
  {
    "rule_id": "no-hardcoded-values",
    "severity": "warning",
    "message": "Hardcoded port number 5000 should be configurable via environment variables.",
    "line": 65,
    "suggestion": "Use os.getenv('PORT', 5000) to allow configuration."
  },
  {
    "rule_id": "no-unsafe-string-concat",
    "severity": "warning",
    "message": "Manual string concatenation in stats endpoint increases risk of malformed JSON.",
    "line": 53,
    "suggestion": "Use dictionary or JSON serialization instead of manual string building."
  },
  {
    "rule_id": "no-nested-conditionals",
    "severity": "warning",
    "message": "Deeply nested conditionals reduce readability in user_handler.",
    "line": 15,
    "suggestion": "Refactor into early returns or separate functions for clarity."
  }
]
```