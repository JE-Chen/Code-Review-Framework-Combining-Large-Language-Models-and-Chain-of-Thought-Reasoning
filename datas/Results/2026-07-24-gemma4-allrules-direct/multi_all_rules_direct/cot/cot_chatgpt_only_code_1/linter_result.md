```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'doStuff' does not follow PEP 8 naming conventions (should be snake_case).",
    "line": 6,
    "suggestion": "Rename to 'do_stuff'."
  },
  {
    "rule_id": "magic-number",
    "severity": "info",
    "message": "Hard-coded constants (3.14159, 2.71828) used instead of named constants or math module constants.",
    "line": 8,
    "suggestion": "Use 'math.pi' and 'math.e'."
  },
  {
    "rule_id": "deeply-nested-logic",
    "severity": "error",
    "message": "Deeply nested conditional logic increases cognitive load and reduces readability.",
    "line": 18,
    "suggestion": "Refactor using guard clauses or split into smaller functions."
  },
  {
    "rule_id": "shared-mutable-state",
    "severity": "error",
    "message": "Use of 'global total_result' introduces hidden coupling and makes the function harder to test.",
    "line": 36,
    "suggestion": "Pass the state explicitly as an argument or encapsulate it in a class."
  },
  {
    "rule_id": "implicit-truthiness",
    "severity": "warning",
    "message": "Implicit truthiness check 'if i or j' can be ambiguous.",
    "line": 41,
    "suggestion": "Use explicit comparisons (e.g., 'if i is not None or j is not None')."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'processEverything' does not follow PEP 8 naming conventions.",
    "line": 46,
    "suggestion": "Rename to 'process_everything'."
  },
  {
    "rule_id": "broad-exception",
    "severity": "error",
    "message": "Bare 'except:' clause catches all exceptions, including SystemExit and KeyboardInterrupt, hiding potential bugs.",
    "line": 56,
    "suggestion": "Catch a specific exception, such as 'ValueError'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable name 'sum' shadows the built-in Python function 'sum()'.",
    "line": 82,
    "suggestion": "Rename to 'total_sum' or similar."
  },
  {
    "rule_id": "performance-bottleneck",
    "severity": "info",
    "message": "Inefficient type conversion: converting a number to a string and then back to a float.",
    "line": 84,
    "suggestion": "Use 'float(sum)' directly."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'collectValues' does not follow PEP 8 naming conventions.",
    "line": 88,
    "suggestion": "Rename to 'collect_values'."
  },
  {
    "rule_id": "mutable-default-argument",
    "severity": "error",
    "message": "Mutable default argument 'bucket=[]' will be shared across all function calls.",
    "line": 88,
    "suggestion": "Use 'bucket=None' and initialize as 'bucket = [] if bucket is None else bucket' inside the function."
  }
]
```