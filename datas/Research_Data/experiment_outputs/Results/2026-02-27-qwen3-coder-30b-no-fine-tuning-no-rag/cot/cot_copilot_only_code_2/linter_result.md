```json
[
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Variable 'val' is defined but not used in the scope.",
    "line": 44,
    "suggestion": "Remove unused variable 'val' or use it in the logic."
  },
  {
    "rule_id": "complexity",
    "severity": "warning",
    "message": "Nested if statements detected, which may reduce readability and increase cognitive load.",
    "line": 37,
    "suggestion": "Refactor nested conditionals into separate functions or simplify logic using early returns."
  },
  {
    "rule_id": "magic-numbers",
    "severity": "warning",
    "message": "Magic number '123456' used directly in code without explanation.",
    "line": 19,
    "suggestion": "Replace magic number with a named constant or configuration value."
  },
  {
    "rule_id": "magic-numbers",
    "severity": "warning",
    "message": "Magic numbers '1234', '5678', and '9999' used directly in code without explanation.",
    "line": 23,
    "suggestion": "Replace magic numbers with named constants or configuration values."
  },
  {
    "rule_id": "no-console",
    "severity": "warning",
    "message": "Use of print() statement is discouraged in production environments.",
    "line": 30,
    "suggestion": "Replace print() calls with logging framework for better control over output."
  }
]
```