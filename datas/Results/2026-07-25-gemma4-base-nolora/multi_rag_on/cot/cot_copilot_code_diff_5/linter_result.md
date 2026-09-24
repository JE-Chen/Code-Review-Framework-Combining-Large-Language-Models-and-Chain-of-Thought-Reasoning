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
    "rule_id": "software-engineering-standard",
    "severity": "error",
    "message": "The function relies on and modifies a global variable 'GLOBAL_DF'. This reduces modularity, makes testing difficult, and can lead to unpredictable state changes.",
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
    "rule_id": "exception-handling",
    "severity": "error",
    "message": "Catching a generic 'Exception' is too broad and hides potential bugs. Additionally, the error message is unprofessional.",
    "line": 27,
    "suggestion": "Catch specific exceptions (e.g., KeyError, TypeError) and provide a meaningful error message."
  }
]
```