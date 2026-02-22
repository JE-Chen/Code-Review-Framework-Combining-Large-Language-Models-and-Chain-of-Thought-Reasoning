```json
[
  {
    "rule_id": "no-global-assign",
    "severity": "error",
    "message": "Assignment to global variable 'GLOBAL_DF' detected. Global state should be avoided.",
    "line": 6,
    "suggestion": "Avoid modifying global variables. Pass data as parameters or return values."
  },
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Unused variable 'ANOTHER_GLOBAL' declared but never used.",
    "line": 7,
    "suggestion": "Remove unused global variable 'ANOTHER_GLOBAL'."
  },
  {
    "rule_id": "function-name-style",
    "severity": "warning",
    "message": "Function name 'functionThatDoesTooMuchAndIsNotClear' does not follow naming convention. It's too long and unclear.",
    "line": 9,
    "suggestion": "Rename function to be more descriptive and concise, e.g., 'analyze_student_data'."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '20' and '50' used in conditional logic. These should be named constants.",
    "line": 17,
    "suggestion": "Define named constants like MIN_AGE_THRESHOLD and MAX_AGE_THRESHOLD."
  },
  {
    "rule_id": "no-bad-exception-handling",
    "severity": "error",
    "message": "Generic exception handling catches all exceptions without specific handling or logging.",
    "line": 21,
    "suggestion": "Catch specific exceptions or at least log them properly instead of ignoring them."
  },
  {
    "rule_id": "no-print-statements",
    "severity": "warning",
    "message": "Use of print statements for output instead of returning results or using proper logging.",
    "line": 19,
    "suggestion": "Replace print statements with return values or use logging for better testability."
  },
  {
    "rule_id": "no-duplicate-code",
    "severity": "warning",
    "message": "Two similar operations on 'Score' column using random integers. Potential duplication.",
    "line": 13,
    "suggestion": "Refactor to reuse logic or create helper functions for generating score adjustments."
  }
]
```