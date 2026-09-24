```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'doSomething' does not follow PEP 8 snake_case convention.",
    "line": 1,
    "suggestion": "Rename to 'do_something'."
  },
  {
    "rule_id": "meaningless-names",
    "severity": "error",
    "message": "Function parameters 'a' through 'j' are non-descriptive and provide no semantic meaning.",
    "line": 1,
    "suggestion": "Use descriptive names that reflect the purpose of the arguments."
  },
  {
    "rule_id": "cognitive-complexity",
    "severity": "warning",
    "message": "Deeply nested conditional blocks (up to 4 levels) reduce readability and maintainability.",
    "line": 3,
    "suggestion": "Use guard clauses or flatten the logic to reduce nesting."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 'dataList' does not follow PEP 8 snake_case convention.",
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
    "rule_id": "cognitive-complexity",
    "severity": "warning",
    "message": "Deeply nested conditional blocks in main() reduce readability.",
    "line": 34,
    "suggestion": "Refactor the logic into a separate function or use a more flat structure."
  }
]
```