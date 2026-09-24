```json
[
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "The variable 'DATA' is a global mutable dictionary. This introduces hidden coupling and makes the code harder to test and reason about.",
    "line": 1,
    "suggestion": "Pass the data as an explicit argument to the functions that need it."
  },
  {
    "rule_id": "single-responsibility",
    "severity": "info",
    "message": "The function 'calculate_average_scores' relies on a global variable and performs both data retrieval and calculation.",
    "line": 21,
    "suggestion": "Refactor the function to accept a list of users as a parameter."
  },
  {
    "rule_id": "deeply-nested-logic",
    "severity": "warning",
    "message": "The 'process_misc' function contains deeply nested conditional logic, increasing cognitive load.",
    "line": 38,
    "suggestion": "Refactor the logic using guard clauses or a mapping strategy to determine the label."
  },
  {
    "rule_id": "deeply-nested-logic",
    "severity": "warning",
    "message": "The 'main' function contains deeply nested if-else blocks for configuration flags.",
    "line": 58,
    "suggestion": "Use guard clauses or flatten the logic to improve readability."
  }
]
```