```json
[
  {
    "rule_id": "no-global-state",
    "severity": "error",
    "message": "Use of global variables (DATA, RESULTS) reduces modularity and testability.",
    "line": 6,
    "suggestion": "Replace global state with function parameters or a class-based approach."
  },
  {
    "rule_id": "no-duplicate-code",
    "severity": "warning",
    "message": "Repeated call to statistics.mean(DATA) and statistics.median(DATA) without caching.",
    "line": 20,
    "suggestion": "Cache results of expensive operations like statistics.mean(DATA) and reuse them."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '37' used for LIMIT without explanation.",
    "line": 9,
    "suggestion": "Define LIMIT as a named constant with a descriptive name."
  },
  {
    "rule_id": "no-implicit-boolean-check",
    "severity": "warning",
    "message": "Implicit boolean check on length comparison may lead to confusion.",
    "line": 16,
    "suggestion": "Explicitly compare length to zero: `if len(DATA) == 0` instead of relying on truthiness."
  },
  {
    "rule_id": "no-hardcoded-ports",
    "severity": "warning",
    "message": "Hardcoded port '5000' in app.run() makes deployment less flexible.",
    "line": 27,
    "suggestion": "Use environment variable or configuration for port setting."
  },
  {
    "rule_id": "no-unvalidated-input",
    "severity": "error",
    "message": "Route endpoints do not validate input parameters which can lead to unexpected behavior or security vulnerabilities.",
    "line": 12,
    "suggestion": "Validate and sanitize all inputs before processing."
  },
  {
    "rule_id": "no-inconsistent-naming",
    "severity": "warning",
    "message": "Inconsistent naming between snake_case ('DATA', 'RESULTS') and camelCase ('meanVal', 'meanAgain').",
    "line": 11,
    "suggestion": "Stick to one naming convention throughout the codebase (prefer snake_case)."
  }
]
```