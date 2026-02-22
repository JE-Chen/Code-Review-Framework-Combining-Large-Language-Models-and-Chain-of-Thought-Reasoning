```json
[
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Variable 'val' is assigned but never used except in conditional checks.",
    "line": 43,
    "suggestion": "Remove unused variable or refactor conditionals to avoid redundancy."
  },
  {
    "rule_id": "complexity",
    "severity": "warning",
    "message": "Nested if statements reduce readability and increase cognitive load.",
    "line": 38,
    "suggestion": "Extract nested conditions into helper functions or simplify logic flow."
  },
  {
    "rule_id": "magic-numbers",
    "severity": "warning",
    "message": "Magic number '123456' used directly in code without explanation.",
    "line": 17,
    "suggestion": "Replace with named constant for better clarity and maintainability."
  },
  {
    "rule_id": "hardcoded-values",
    "severity": "warning",
    "message": "String literal 'weird' appears to be a hardcoded configuration value.",
    "line": 41,
    "suggestion": "Use a predefined enum or constant for configuration values."
  },
  {
    "rule_id": "inconsistent-naming",
    "severity": "warning",
    "message": "Class name 'DataPipeline' does not follow snake_case naming convention.",
    "line": 19,
    "suggestion": "Rename class to 'data_pipeline' for consistency with Python conventions."
  }
]
```