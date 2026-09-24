```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'doStuff' does not follow PEP 8 snake_case convention.",
    "line": 6,
    "suggestion": "Rename to 'do_stuff'."
  },
  {
    "rule_id": "too-many-arguments",
    "severity": "warning",
    "message": "Function 'doStuff' has too many arguments (10), which reduces readability and maintainability.",
    "line": 6,
    "suggestion": "Group related parameters into a data class or dictionary."
  },
  {
    "rule_id": "deeply-nested-logic",
    "severity": "warning",
    "message": "Excessive nesting of if-statements (5 levels) makes the logic difficult to follow.",
    "line": 21,
    "suggestion": "Use guard clauses or a lookup table to flatten the logic."
  },
  {
    "rule_id": "redundant-logic",
    "severity": "info",
    "message": "The operations 'temp1 = z + 1' and 'temp2 = temp1 - 1' are redundant and cancel each other out.",
    "line": 38,
    "suggestion": "Assign 'result = z' directly."
  },
  {
    "rule_id": "global-variable-usage",
    "severity": "warning",
    "message": "Use of 'global total_result' creates hidden dependencies and makes the function harder to test.",
    "line": 42,
    "suggestion": "Pass the accumulator as an argument or return the value to be summed externally."
  },
  {
    "rule_id": "unused-parameters",
    "severity": "info",
    "message": "Parameters 'i' and 'j' are checked but their result is not used (pass).",
    "line": 47,
    "suggestion": "Remove unused parameters if they serve no functional purpose."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'processEverything' does not follow PEP 8 snake_case convention.",
    "line": 52,
    "suggestion": "Rename to 'process_everything'."
  },
  {
    "rule_id": "type-checking-style",
    "severity": "info",
    "message": "Using 'type(item) == int' is less flexible than 'isinstance(item, int)'.",
    "line": 56,
    "suggestion": "Use 'isinstance(item, int)'."
  },
  {
    "rule_id": "bare-except",
    "severity": "error",
    "message": "Bare 'except:' clause catches all exceptions, including SystemExit and KeyboardInterrupt.",
    "line": 62,
    "suggestion": "Catch a specific exception, e.g., 'except ValueError:'."
  },
  {
    "rule_id": "shadowing-builtin",
    "severity": "warning",
    "message": "Variable 'sum' shadows the built-in Python function 'sum()'.",
    "line": 86,
    "suggestion": "Rename 'sum' to 'total_sum' or similar."
  },
  {
    "rule_id": "inefficient-conversion",
    "severity": "info",
    "message": "Converting a number to a string and then back to a float 'float(str(sum))' is inefficient and unnecessary.",
    "line": 88,
    "suggestion": "Use 'float(sum)'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'collectValues' does not follow PEP 8 snake_case convention.",
    "line": 92,
    "suggestion": "Rename to 'collect_values'."
  },
  {
    "rule_id": "mutable-default-argument",
    "severity": "error",
    "message": "Using a mutable default argument 'bucket=[]' can lead to unexpected behavior as the list is shared across calls.",
    "line": 92,
    "suggestion": "Set 'bucket=None' and initialize as 'bucket = [] if bucket is None else bucket' inside the function."
  }
]
```