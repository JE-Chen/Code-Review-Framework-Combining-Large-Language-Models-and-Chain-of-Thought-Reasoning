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
    "rule_id": "meaningful-names",
    "severity": "error",
    "message": "Function parameters 'a' through 'j' are non-descriptive and lack semantic meaning.",
    "line": 1,
    "suggestion": "Rename parameters to reflect the data they represent."
  },
  {
    "rule_id": "software-engineering-standards",
    "severity": "warning",
    "message": "Deeply nested conditional logic (arrow code) reduces readability and maintainability.",
    "line": 3,
    "suggestion": "Use guard clauses or flatten the logic to reduce nesting levels."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 'dataList' uses camelCase; Python convention (PEP 8) prescribes snake_case.",
    "line": 21,
    "suggestion": "Rename to 'data_list'."
  },
  {
    "rule_id": "software-engineering-standards",
    "severity": "info",
    "message": "Iterating using 'range(len(...))' is an anti-pattern in Python.",
    "line": 25,
    "suggestion": "Iterate directly over the list: 'for item in dataList:'."
  },
  {
    "rule_id": "meaningful-names",
    "severity": "warning",
    "message": "Variable 'x' is too generic for a result accumulator.",
    "line": 24,
    "suggestion": "Rename to something descriptive, e.g., 'total_sum'."
  },
  {
    "rule_id": "software-engineering-standards",
    "severity": "warning",
    "message": "Deeply nested conditional logic in main() reduces readability.",
    "line": 34,
    "suggestion": "Refactor the range-checking logic into a separate function or use a more flat structure."
  }
]
```