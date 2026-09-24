```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 'DATAFRAME' uses SCREAMING_SNAKE_CASE, which is typically reserved for constants, but it is being mutated globally.",
    "line": 5,
    "suggestion": "Rename to 'dataframe' or 'df' to follow PEP 8 variable naming conventions."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 'resultList' uses camelCase, which is not the standard for Python variables.",
    "line": 6,
    "suggestion": "Rename to 'result_list' to follow snake_case convention."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 'tempStorage' uses camelCase, which is not the standard for Python variables.",
    "line": 7,
    "suggestion": "Rename to 'temp_storage' to follow snake_case convention."
  },
  {
    "rule_id": "software-engineering-standard",
    "severity": "error",
    "message": "Excessive use of 'global' keywords. This makes the code harder to test, maintain, and prone to side-effect bugs.",
    "line": 10,
    "suggestion": "Pass data as arguments to functions and return results instead of modifying global state."
  },
  {
    "rule_id": "software-engineering-standard",
    "severity": "error",
    "message": "Excessive use of 'global' keywords. This makes the code harder to test, maintain, and prone to side-effect bugs.",
    "line": 18,
    "suggestion": "Pass data as arguments to functions and return results instead of modifying global state."
  },
  {
    "rule_id": "duplicate-code",
    "severity": "warning",
    "message": "Redundant calculation of 'st.mean(DATAFRAME[col])' for column 'A'.",
    "line": 23,
    "suggestion": "Reuse the 'meanA' variable already calculated on line 21."
  },
  {
    "rule_id": "software-engineering-standard",
    "severity": "error",
    "message": "Excessive use of 'global' keywords. This makes the code harder to test, maintain, and prone to side-effect bugs.",
    "line": 32,
    "suggestion": "Pass data as arguments to functions and return results instead of modifying global state."
  }
]
```