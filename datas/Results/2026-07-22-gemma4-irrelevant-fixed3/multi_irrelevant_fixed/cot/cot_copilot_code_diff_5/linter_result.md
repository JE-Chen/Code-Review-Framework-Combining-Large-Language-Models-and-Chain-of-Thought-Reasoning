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
    "message": "Use of 'global' keyword to modify 'GLOBAL_DF' creates hidden dependencies and makes the code harder to test and maintain.",
    "line": 9,
    "suggestion": "Pass the DataFrame as an argument to the function and return the modified DataFrame."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "warning",
    "message": "Deeply nested if-else blocks reduce readability and maintainability.",
    "line": 21,
    "suggestion": "Use guard clauses or a more flattened logic structure to handle age range checks."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "error",
    "message": "Catching a generic 'Exception' and printing a non-descriptive message hides potential bugs and makes debugging difficult.",
    "line": 27,
    "suggestion": "Catch specific exceptions (e.g., KeyError, TypeError) and provide meaningful error logging."
  },
  {
    "rule_id": "software-engineering-standards",
    "severity": "info",
    "message": "The function performs multiple unrelated tasks: data creation, data transformation, and reporting.",
    "line": 8,
    "suggestion": "Split the function into smaller, modular functions (e.g., 'load_data', 'transform_data', 'print_report')."
  }
]
```