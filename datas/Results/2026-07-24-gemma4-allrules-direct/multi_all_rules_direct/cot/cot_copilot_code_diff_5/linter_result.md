```json
[
  {
    "rule_id": "shared-mutable-state",
    "severity": "error",
    "message": "Use of global variable 'GLOBAL_DF' introduces hidden coupling and makes the code harder to test and reason about.",
    "line": 4,
    "suggestion": "Pass the DataFrame as an argument to functions and return the modified result instead of using a global variable."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'functionThatDoesTooMuchAndIsNotClear' does not follow Python's snake_case naming convention and is not descriptive of its actual purpose.",
    "line": 7,
    "suggestion": "Rename the function to something descriptive using snake_case, e.g., 'analyze_student_scores'."
  },
  {
    "rule_id": "single-responsibility",
    "severity": "warning",
    "message": "The function performs data creation, transformation, analysis, and I/O (printing), violating the single responsibility principle.",
    "line": 7,
    "suggestion": "Split the function into smaller, focused functions: one for data loading, one for transformation, and one for reporting."
  },
  {
    "rule_id": "deeply-nested-conditionals",
    "severity": "info",
    "message": "Deeply nested conditional logic increases cognitive load.",
    "line": 21,
    "suggestion": "Use guard clauses or a flatter structure to simplify the control flow."
  },
  {
    "rule_id": "broad-exception-handling",
    "severity": "error",
    "message": "Catching a broad 'Exception' can hide unexpected bugs and makes debugging difficult.",
    "line": 27,
    "suggestion": "Catch specific exceptions (e.g., KeyError, TypeError) that are expected during the mean calculation."
  }
]
```