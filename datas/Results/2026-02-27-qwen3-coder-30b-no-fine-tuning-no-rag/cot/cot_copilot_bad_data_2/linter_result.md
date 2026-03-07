```json
[
  {
    "rule_id": "no-console",
    "severity": "warning",
    "message": "Use of print() detected; consider using logging instead for better control over output.",
    "line": 4,
    "suggestion": "Replace print() with logging.debug() or logging.info()."
  },
  {
    "rule_id": "no-console",
    "severity": "warning",
    "message": "Use of print() detected; consider using logging instead for better control over output.",
    "line": 6,
    "suggestion": "Replace print() with logging.debug() or logging.info()."
  },
  {
    "rule_id": "no-console",
    "severity": "warning",
    "message": "Use of print() detected; consider using logging instead for better control over output.",
    "line": 9,
    "suggestion": "Replace print() with logging.debug() or logging.info()."
  },
  {
    "rule_id": "no-console",
    "severity": "warning",
    "message": "Use of print() detected; consider using logging instead for better control over output.",
    "line": 11,
    "suggestion": "Replace print() with logging.debug() or logging.info()."
  },
  {
    "rule_id": "no-console",
    "severity": "warning",
    "message": "Use of print() detected; consider using logging instead for better control over output.",
    "line": 18,
    "suggestion": "Replace print() with logging.debug() or logging.info()."
  },
  {
    "rule_id": "no-console",
    "severity": "warning",
    "message": "Use of print() detected; consider using logging instead for better control over output.",
    "line": 20,
    "suggestion": "Replace print() with logging.debug() or logging.info()."
  },
  {
    "rule_id": "no-global-assign",
    "severity": "error",
    "message": "Assignment to global variable 'global_config' detected; avoid modifying globals when possible.",
    "line": 15,
    "suggestion": "Pass configuration as a parameter or use a configuration manager."
  },
  {
    "rule_id": "no-eval",
    "severity": "error",
    "message": "Use of eval() detected; this can lead to security vulnerabilities if user input is not properly sanitized.",
    "line": 24,
    "suggestion": "Avoid using eval(); consider safer alternatives like ast.literal_eval() or a proper parser."
  },
  {
    "rule_id": "no-unsafe-assignment",
    "severity": "error",
    "message": "Potentially unsafe assignment in risky_update; catch specific exceptions instead of generic Exception.",
    "line": 27,
    "suggestion": "Catch more specific exceptions such as KeyError or TypeError rather than broad Exception."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '7' used in function 'f'; consider defining it as a named constant.",
    "line": 21,
    "suggestion": "Define '7' as a named constant or parameter for clarity."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '13' used in function 'f'; consider defining it as a named constant.",
    "line": 21,
    "suggestion": "Define '13' as a named constant or parameter for clarity."
  },
  {
    "rule_id": "no-duplicate-functions",
    "severity": "warning",
    "message": "Function 'check_value' duplicates behavior of conditional expression; could be simplified.",
    "line": 13,
    "suggestion": "Simplify logic by returning directly from condition check."
  },
  {
    "rule_id": "no-unexpected-side-effects",
    "severity": "warning",
    "message": "Function 'secret_behavior' has side effect through 'hidden_flag' global variable usage.",
    "line": 10,
    "suggestion": "Avoid relying on global state; pass dependencies explicitly."
  }
]
```