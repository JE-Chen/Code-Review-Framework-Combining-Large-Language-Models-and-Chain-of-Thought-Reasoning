```json
[
  {
    "rule_id": "no-global-state",
    "severity": "warning",
    "message": "Use of global variables (DATA_STORE, USER_COUNT) reduces modularity and testability.",
    "line": 5,
    "suggestion": "Replace global state with a class-based approach or dependency injection."
  },
  {
    "rule_id": "no-raw-exceptions",
    "severity": "error",
    "message": "Catching generic Exception may hide unexpected errors and makes debugging harder.",
    "line": 18,
    "suggestion": "Catch specific exceptions such as ValueError or TypeError instead of broad Exception."
  },
  {
    "rule_id": "no-duplicate-code",
    "severity": "warning",
    "message": "Duplicate logic in handling item values in /items route can be abstracted into a helper function.",
    "line": 26,
    "suggestion": "Extract common logic into a reusable function to reduce redundancy."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '100' used in conditional checks without explanation.",
    "line": 46,
    "suggestion": "Define '100' as a named constant for better readability and maintainability."
  },
  {
    "rule_id": "no-hardcoded-config",
    "severity": "warning",
    "message": "Hardcoded configuration values like 'mode': 'test' and 'threshold': 123 make the application less flexible.",
    "line": 6,
    "suggestion": "Externalize configurations using environment variables or config files."
  },
  {
    "rule_id": "no-nested-conditionals",
    "severity": "warning",
    "message": "Deeply nested conditionals in /complex route reduce readability and increase complexity.",
    "line": 41,
    "suggestion": "Refactor nested conditions using early returns or helper functions."
  },
  {
    "rule_id": "no-unvalidated-input",
    "severity": "warning",
    "message": "Direct use of request parameters without sanitization may lead to security vulnerabilities.",
    "line": 44,
    "suggestion": "Validate and sanitize all input from external sources before processing."
  }
]
```