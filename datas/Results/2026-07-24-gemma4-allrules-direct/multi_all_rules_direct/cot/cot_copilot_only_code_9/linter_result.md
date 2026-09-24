```json
[
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "Use of global mutable state 'GLOBAL_RESULTS' can introduce hidden coupling and make the code harder to test.",
    "line": 5,
    "suggestion": "Pass the results list as an argument to functions or return values from 'process_data' and pass them to 'main'."
  },
  {
    "rule_id": "broad-exception",
    "severity": "warning",
    "message": "Catching broad 'Exception' can hide unexpected bugs and make debugging difficult.",
    "line": 11,
    "suggestion": "Catch specific exceptions, such as 'requests.exceptions.RequestException'."
  },
  {
    "rule_id": "broad-exception",
    "severity": "warning",
    "message": "Catching broad 'Exception' can hide unexpected bugs and make debugging difficult.",
    "line": 18,
    "suggestion": "Catch specific exceptions, such as 'requests.exceptions.RequestException'."
  },
  {
    "rule_id": "broad-exception",
    "severity": "warning",
    "message": "Catching broad 'Exception' can hide unexpected bugs and make debugging difficult.",
    "line": 25,
    "suggestion": "Catch specific exceptions, such as 'requests.exceptions.RequestException'."
  },
  {
    "rule_id": "descriptive-naming",
    "severity": "info",
    "message": "Variable names 'u', 'p', and 'c' are too short and not descriptive.",
    "line": 33,
    "suggestion": "Use 'user', 'post', and 'comment' instead."
  },
  {
    "rule_id": "deeply-nested-logic",
    "severity": "warning",
    "message": "Deeply nested conditional logic increases cognitive load.",
    "line": 48,
    "suggestion": "Use guard clauses or a flatter if-elif-else structure to simplify the logic."
  }
]
```