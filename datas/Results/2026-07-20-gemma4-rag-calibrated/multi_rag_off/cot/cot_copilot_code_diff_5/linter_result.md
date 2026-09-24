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
    "message": "Use of 'global' keyword to modify 'GLOBAL_DF' creates tight coupling and makes the code harder to test and maintain.",
    "line": 9,
    "suggestion": "Pass the DataFrame as an argument to the function and return the modified DataFrame."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "info",
    "message": "The logic for 'ScorePlusRandom' and 'ScorePlusRandomAgain' applies the same random integer to the entire column rather than generating a unique random value per row.",
    "line": 16,
    "suggestion": "Use 'numpy.random.randint' or a list comprehension to generate unique values for each row."
  },
  {
    "rule_id": "readability-consistency",
    "severity": "warning",
    "message": "Deeply nested if-else blocks reduce readability.",
    "line": 20,
    "suggestion": "Flatten the logic using 'elif' statements."
  },
  {
    "rule_id": "exception-handling",
    "severity": "error",
    "message": "Catching a generic 'Exception' and printing a vague message ('我不管錯誤是什麼') hides potential bugs and makes debugging difficult.",
    "line": 26,
    "suggestion": "Catch specific exceptions (e.g., KeyError, TypeError) and provide meaningful error logging."
  }
]
```