```json
[
  {
    "rule_id": "no-global-state",
    "severity": "error",
    "message": "Use of global variables (DATA, RESULTS) reduces testability and modularity.",
    "line": 6,
    "suggestion": "Replace globals with local state or dependency injection."
  },
  {
    "rule_id": "no-duplicate-code",
    "severity": "warning",
    "message": "Repeated call to `statistics.mean(DATA)` and `statistics.median(DATA)` without caching.",
    "line": 20,
    "suggestion": "Cache computed values to avoid redundant calculations."
  },
  {
    "rule_id": "no-implicit-logic",
    "severity": "warning",
    "message": "Logic assumes specific array sizes for condition checks but does not validate inputs.",
    "line": 18,
    "suggestion": "Add explicit input validation or ensure size constraints are enforced elsewhere."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '37' used for LIMIT without explanation.",
    "line": 9,
    "suggestion": "Define LIMIT as a named constant with context."
  },
  {
    "rule_id": "no-unchecked-input",
    "severity": "error",
    "message": "The application does not sanitize or validate user-provided input from routes.",
    "line": 13,
    "suggestion": "Validate and sanitize all inputs before processing."
  },
  {
    "rule_id": "no-hardcoded-ports",
    "severity": "warning",
    "message": "Hardcoded port '5000' makes deployment less flexible.",
    "line": 27,
    "suggestion": "Use environment variables for configuration like PORT."
  }
]
```