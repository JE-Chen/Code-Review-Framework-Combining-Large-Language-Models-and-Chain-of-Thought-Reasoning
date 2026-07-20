```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'functionThatDoesTooMuchAndIsNotClear' uses camelCase, which violates PEP 8 naming conventions for Python functions (should be snake_case).",
    "line": 8,
    "suggestion": "Rename to 'analyze_data' or a similar descriptive snake_case name."
  },
  {
    "rule_id": "software-engineering-standards",
    "severity": "error",
    "message": "The function relies on and modifies a global variable 'GLOBAL_DF', which reduces modularity and makes the code harder to test and maintain.",
    "line": 9,
    "suggestion": "Pass the DataFrame as an argument to the function and return the modified DataFrame instead of using the 'global' keyword."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "warning",
    "message": "The nested if-else structure for 'mean_age' is overly complex and can be simplified.",
    "line": 21,
    "suggestion": "Use 'elif' to flatten the conditional logic."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "error",
    "message": "Catching a generic 'Exception' and printing a vague message ('我不管錯誤是什麼') hides potential bugs and makes debugging difficult.",
    "line": 27,
    "suggestion": "Catch specific exceptions (e.g., KeyError, TypeError) and provide meaningful error handling or logging."
  }
]
```