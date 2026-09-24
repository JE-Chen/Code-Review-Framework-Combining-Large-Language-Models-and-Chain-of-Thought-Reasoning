```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'doSomething' uses camelCase; Python convention (PEP 8) prescribes snake_case.",
    "line": 1,
    "suggestion": "Rename to 'do_something'."
  },
  {
    "rule_id": "meaningless-names",
    "severity": "error",
    "message": "Function parameters 'a' through 'j' are non-descriptive and provide no semantic meaning.",
    "line": 1,
    "suggestion": "Use descriptive names that reflect the purpose of each argument."
  },
  {
    "rule_id": "cognitive-complexity",
    "severity": "warning",
    "message": "Deeply nested if-statements (4 levels) reduce readability and maintainability.",
    "line": 3,
    "suggestion": "Use guard clauses or combine conditions to flatten the structure."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 'dataList' uses camelCase; Python convention (PEP 8) prescribes snake_case.",
    "line": 21,
    "suggestion": "Rename to 'data_list'."
  },
  {
    "rule_id": "software-engineering-standard",
    "severity": "info",
    "message": "Iterating using 'range(len(...))' is an anti-pattern in Python.",
    "line": 25,
    "suggestion": "Iterate directly over the list: 'for item in dataList:'."
  },
  {
    "rule_id": "meaningless-names",
    "severity": "warning",
    "message": "Variable 'x' is non-descriptive.",
    "line": 24,
    "suggestion": "Rename to something descriptive, e.g., 'total_sum'."
  },
  {
    "rule_id": "cognitive-complexity",
    "severity": "warning",
    "message": "Deeply nested if-statements in main() reduce readability.",
    "line": 34,
    "suggestion": "Refactor the logic into a separate function or use a more flat conditional structure."
  }
]
```