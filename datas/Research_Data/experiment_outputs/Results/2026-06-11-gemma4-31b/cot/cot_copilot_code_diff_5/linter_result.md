```json
[
  {
    "rule_id": "naming-convention",
    "severity": "error",
    "message": "Function name 'functionThatDoesTooMuchAndIsNotClear' uses camelCase instead of snake_case and is overly descriptive of its flaws rather than its intent.",
    "line": 8,
    "suggestion": "Rename to something descriptive of the business logic, e.g., 'analyze_student_scores()', using snake_case."
  },
  {
    "rule_id": "software-engineering-standards",
    "severity": "error",
    "message": "Use of global variable 'GLOBAL_DF' creates hidden dependencies and makes the code harder to test and maintain.",
    "line": 9,
    "suggestion": "Pass the DataFrame as an argument to the function and return the results instead of using 'global'."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "warning",
    "message": "The logic for adding random values to 'ScorePlusRandom' and 'ScorePlusRandomAgain' applies a single random integer to the entire column rather than per-row, which may not be the intended behavior for data augmentation.",
    "line": 16,
    "suggestion": "Use a vectorized approach or a lambda function if per-row randomness is required."
  },
  {
    "rule_id": "readability-consistency",
    "severity": "info",
    "message": "Deeply nested if-else statements reduce readability (Arrow anti-pattern).",
    "line": 20,
    "suggestion": "Use guard clauses or a flatter conditional structure to improve clarity."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "error",
    "message": "Broad exception handling 'except Exception as e' catches all errors, making debugging difficult and potentially masking critical bugs.",
    "line": 27,
    "suggestion": "Catch specific exceptions (e.g., KeyError, TypeError) and use a proper logging framework instead of print statements."
  },
  {
    "rule_id": "naming-convention",
    "severity": "info",
    "message": "Variable 'ANOTHER_GLOBAL' is a vague name that does not describe the content or purpose of the string.",
    "line": 5,
    "suggestion": "Rename to something meaningful, e.g., 'START_MESSAGE'."
  },
  {
    "rule_id": "documentation-testing",
    "severity": "warning",
    "message": "The module lacks docstrings and type hints, making it difficult for other developers to understand the input/output expectations.",
    "line": 8,
    "suggestion": "Add a Google or NumPy style docstring to the function and define type hints (e.g., '-> None')."
  }
]
```