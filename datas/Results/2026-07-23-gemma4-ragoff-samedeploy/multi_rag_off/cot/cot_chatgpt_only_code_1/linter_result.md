```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'doStuff' does not follow PEP 8 snake_case convention and is not descriptive.",
    "line": 6,
    "suggestion": "Rename to something descriptive like 'calculate_value' using snake_case."
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
    "message": "Excessive nesting of if-statements (5 levels deep) makes the logic hard to follow.",
    "line": 18,
    "suggestion": "Use guard clauses or a lookup table to flatten the logic."
  },
  {
    "rule_id": "redundant-logic",
    "severity": "info",
    "message": "The operations 'temp1 = z + 1' and 'temp2 = temp1 - 1' are redundant as they cancel each other out.",
    "line": 34,
    "suggestion": "Assign 'result = z' directly."
  },
  {
    "rule_id": "global-variable-usage",
    "severity": "warning",
    "message": "Use of 'global total_result' creates hidden dependencies and makes the function harder to test.",
    "line": 38,
    "suggestion": "Pass the accumulator as an argument or return the value to be summed externally."
  },
  {
    "rule_id": "unused-logic",
    "severity": "info",
    "message": "The conditional 'if i or j: pass' performs no action.",
    "line": 43,
    "suggestion": "Remove the unused conditional block."
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
    "message": "Bare 'except:' clause catches all exceptions, including SystemExit and KeyboardInterrupt, which can hide bugs.",
    "line": 58,
    "suggestion": "Catch a specific exception, such as 'ValueError'."
  },
  {
    "rule_id": "shadowing-builtin",
    "severity": "warning",
    "message": "Variable 'sum' shadows the built-in Python function 'sum()'.",
    "line": 83,
    "suggestion": "Rename the variable to 'total_sum' or similar."
  },
  {
    "rule_id": "inefficient-conversion",
    "severity": "info",
    "message": "Converting a number to a string and then back to a float 'float(str(sum))' is inefficient and unnecessary.",
    "line": 85,
    "suggestion": "Use 'float(sum)'."
  },
  {
    "rule_id": "mutable-default-argument",
    "severity": "error",
    "message": "Using a mutable default argument 'bucket=[]' leads to shared state across function calls.",
    "line": 89,
    "suggestion": "Set 'bucket=None' and initialize as 'bucket = [] if bucket is None else bucket' inside the function."
  }
]
```