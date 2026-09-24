```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'doStuff' does not follow PEP 8 naming conventions (should be snake_case).",
    "line": 6,
    "suggestion": "Rename to 'do_stuff' or a more descriptive name."
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
    "message": "Excessive nesting of if-statements (5 levels deep) makes the logic difficult to follow.",
    "line": 18,
    "suggestion": "Use guard clauses or a lookup table to flatten the logic."
  },
  {
    "rule_id": "redundant-assignment",
    "severity": "info",
    "message": "Variables 'temp1' and 'temp2' are redundant as they perform a net-zero operation.",
    "line": 36,
    "suggestion": "Simplify to 'result = z'."
  },
  {
    "rule_id": "global-variable-usage",
    "severity": "warning",
    "message": "Use of 'global total_result' creates hidden dependencies and makes the function harder to test.",
    "line": 40,
    "suggestion": "Pass the accumulator as an argument or return the value to be summed externally."
  },
  {
    "rule_id": "unused-parameters",
    "severity": "info",
    "message": "Parameters 'i' and 'j' are checked but their result is not used (pass).",
    "line": 46,
    "suggestion": "Remove parameters if they serve no functional purpose."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'processEverything' does not follow PEP 8 naming conventions (should be snake_case).",
    "line": 51,
    "suggestion": "Rename to 'process_everything'."
  },
  {
    "rule_id": "type-checking-anti-pattern",
    "severity": "info",
    "message": "Using 'type(item) == int' is less flexible than 'isinstance(item, int)'.",
    "line": 55,
    "suggestion": "Use 'isinstance(item, int)'."
  },
  {
    "rule_id": "bare-except",
    "severity": "error",
    "message": "Bare 'except:' clause catches all exceptions, including SystemExit and KeyboardInterrupt.",
    "line": 61,
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
    "rule_id": "inefficient-type-conversion",
    "severity": "info",
    "message": "Converting a number to a string and then back to a float is inefficient.",
    "line": 88,
    "suggestion": "Use 'float(sum)' directly."
  },
  {
    "rule_id": "mutable-default-argument",
    "severity": "error",
    "message": "Using a mutable default argument 'bucket=[]' can lead to unexpected behavior across function calls.",
    "line": 92,
    "suggestion": "Use 'bucket=None' and initialize inside the function: 'if bucket is None: bucket = []'."
  }
]
```