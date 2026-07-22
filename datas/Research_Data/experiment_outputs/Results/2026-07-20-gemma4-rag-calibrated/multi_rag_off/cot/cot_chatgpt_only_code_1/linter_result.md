```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'doStuff' does not follow PEP 8 snake_case convention and is not descriptive.",
    "line": 6,
    "suggestion": "Rename to 'calculate_value' or a more descriptive name using snake_case."
  },
  {
    "rule_id": "too-many-arguments",
    "severity": "warning",
    "message": "Function 'doStuff' has too many parameters (10), which reduces readability and maintainability.",
    "line": 6,
    "suggestion": "Group related parameters into a data class or dictionary."
  },
  {
    "rule_id": "deeply-nested-logic",
    "severity": "warning",
    "message": "Excessive nesting of if-statements (5 levels) makes the logic difficult to follow.",
    "line": 18,
    "suggestion": "Use guard clauses or a lookup table to flatten the logic."
  },
  {
    "rule_id": "global-variable-usage",
    "severity": "error",
    "message": "Use of 'global total_result' creates hidden dependencies and makes the function harder to test.",
    "line": 38,
    "suggestion": "Pass the accumulator as an argument or return the value to be summed by the caller."
  },
  {
    "rule_id": "unused-parameters",
    "severity": "info",
    "message": "Parameters 'i' and 'j' are checked but their values do not affect the outcome of the function.",
    "line": 43,
    "suggestion": "Remove unused parameters if they serve no functional purpose."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'processEverything' does not follow PEP 8 snake_case convention.",
    "line": 48,
    "suggestion": "Rename to 'process_everything'."
  },
  {
    "rule_id": "type-checking-style",
    "severity": "info",
    "message": "Using 'type(item) == int' is less flexible than 'isinstance(item, int)'.",
    "line": 52,
    "suggestion": "Use 'isinstance(item, int)'."
  },
  {
    "rule_id": "bare-except",
    "severity": "error",
    "message": "Bare 'except:' clause catches all exceptions, including SystemExit and KeyboardInterrupt.",
    "line": 58,
    "suggestion": "Catch a specific exception, e.g., 'except ValueError:'."
  },
  {
    "rule_id": "shadowing-builtin",
    "severity": "warning",
    "message": "Variable 'sum' shadows the built-in Python function 'sum()'.",
    "line": 83,
    "suggestion": "Rename 'sum' to 'total_sum' or similar."
  },
  {
    "rule_id": "inefficient-conversion",
    "severity": "info",
    "message": "Converting a number to a string and then back to a float 'float(str(sum))' is redundant.",
    "line": 85,
    "suggestion": "Use 'float(sum)' directly."
  },
  {
    "rule_id": "mutable-default-argument",
    "severity": "error",
    "message": "Using a mutable default argument 'bucket=[]' can lead to unexpected behavior across function calls.",
    "line": 89,
    "suggestion": "Use 'bucket=None' and initialize inside the function: 'if bucket is None: bucket = []'."
  }
]
```