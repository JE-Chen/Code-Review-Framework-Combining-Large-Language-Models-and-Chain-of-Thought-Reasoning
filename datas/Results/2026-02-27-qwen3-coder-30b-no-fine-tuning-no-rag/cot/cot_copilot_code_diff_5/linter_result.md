```json
[
  {
    "rule_id": "no-global-assign",
    "severity": "error",
    "message": "Assignment to global variable 'GLOBAL_DF' detected. Global variables should be avoided to maintain modularity and testability.",
    "line": 7,
    "suggestion": "Refactor to avoid modifying global state; pass data as parameters or return values instead."
  },
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Unused global variable 'ANOTHER_GLOBAL' declared but never used in the code.",
    "line": 8,
    "suggestion": "Remove unused global variable 'ANOTHER_GLOBAL' if it's not needed."
  },
  {
    "rule_id": "function-max-lines",
    "severity": "error",
    "message": "Function 'functionThatDoesTooMuchAndIsNotClear' exceeds recommended maximum lines. It performs multiple unrelated tasks.",
    "line": 5,
    "suggestion": "Break down this function into smaller, focused functions that each handle one responsibility."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '20' and '50' used directly in conditional logic. These should be replaced with named constants for clarity.",
    "line": 16,
    "suggestion": "Define named constants like MIN_AGE = 20 and MAX_AGE = 50 to improve readability."
  },
  {
    "rule_id": "no-bad-exception-handling",
    "severity": "error",
    "message": "Generic exception handling with broad 'except Exception as e' can mask unexpected errors and make debugging difficult.",
    "line": 19,
    "suggestion": "Catch specific exceptions or at least log the actual error type for better diagnostics."
  },
  {
    "rule_id": "no-duplicated-code",
    "severity": "warning",
    "message": "Duplicated logic for adding random scores to the DataFrame. This pattern appears twice with minor variation.",
    "line": 13,
    "suggestion": "Extract the score addition logic into a helper function to reduce duplication."
  },
  {
    "rule_id": "no-unscoped-variables",
    "severity": "error",
    "message": "Use of global keyword indicates lack of encapsulation. Global variables introduce tight coupling and side effects.",
    "line": 6,
    "suggestion": "Avoid using global variables by passing required data through parameters or returning results explicitly."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'functionThatDoesTooMuchAndIsNotClear' does not follow naming conventions and is too verbose.",
    "line": 5,
    "suggestion": "Rename function to something more descriptive and concise, such as 'analyze_age_and_scores'."
  }
]
```