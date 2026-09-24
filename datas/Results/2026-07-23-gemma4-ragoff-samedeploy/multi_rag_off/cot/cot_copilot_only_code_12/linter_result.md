```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 'DATAFRAME' uses SCREAMING_SNAKE_CASE, which is typically reserved for constants, but it is being mutated as a global variable.",
    "line": 6,
    "suggestion": "Rename to 'dataframe' or 'df' to follow PEP 8 naming conventions for variables."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 'resultList' uses camelCase, which is inconsistent with Python's snake_case convention.",
    "line": 7,
    "suggestion": "Rename to 'result_list'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 'tempStorage' uses camelCase, which is inconsistent with Python's snake_case convention.",
    "line": 8,
    "suggestion": "Rename to 'temp_storage'."
  },
  {
    "rule_id": "software-engineering-standard",
    "severity": "error",
    "message": "Excessive use of 'global' variables ('DATAFRAME', 'resultList') creates tight coupling and makes the code harder to test and maintain.",
    "line": 11,
    "suggestion": "Pass data as arguments to functions and return results instead of modifying global state."
  },
  {
    "rule_id": "software-engineering-standard",
    "severity": "warning",
    "message": "Duplicate logic: 'st.mean(DATAFRAME[col])' is called twice for column 'A' and appended to the result list twice.",
    "line": 23,
    "suggestion": "Calculate the mean once and reuse the variable."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "info",
    "message": "The 'tempStorage' dictionary is populated but never read from, making it dead code.",
    "line": 22,
    "suggestion": "Remove 'tempStorage' if it serves no purpose in the application logic."
  }
]
```