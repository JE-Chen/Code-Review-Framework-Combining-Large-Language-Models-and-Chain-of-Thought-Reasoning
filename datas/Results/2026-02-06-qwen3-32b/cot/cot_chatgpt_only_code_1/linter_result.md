[
  {
    "rule_id": "global-variable",
    "severity": "error",
    "message": "Global variable `total_result` is used, creating hidden coupling and breaking testability.",
    "line": 43,
    "suggestion": "Remove global state; return the result and accumulate in the caller."
  },
  {
    "rule_id": "mutable-default",
    "severity": "error",
    "message": "Mutable default argument `bucket=[]` is shared across all function calls, causing unexpected behavior.",
    "line": 101,
    "suggestion": "Use `None` as the default and initialize the list inside the function."
  },
  {
    "rule_id": "poor-naming",
    "severity": "warning",
    "message": "Parameter names are non-descriptive (e.g., 'a', 'b', 'c'). Use meaningful names for clarity.",
    "line": 6,
    "suggestion": "Rename parameters to reflect their purpose (e.g., `input_value`, `shape_type`)."
  },
  {
    "rule_id": "too-many-params",
    "severity": "warning",
    "message": "Function has 10 parameters, which is too many for maintainability and testability.",
    "line": 6,
    "suggestion": "Group related parameters into a data structure or reduce the number of parameters."
  },
  {
    "rule_id": "deep-nesting",
    "severity": "warning",
    "message": "Deeply nested conditionals (7 levels) make code hard to read and test.",
    "line": 19,
    "suggestion": "Refactor conditionals to reduce nesting (e.g., early returns or guard clauses)."
  },
  {
    "rule_id": "redundant-calc",
    "severity": "warning",
    "message": "Redundant calculations: `temp1 = z + 1` and `temp2 = temp1 - 1` are equivalent to `z`.",
    "line": 39,
    "suggestion": "Replace with `result = z`."
  },
  {
    "rule_id": "unnecessary-sleep",
    "severity": "warning",
    "message": "Unnecessary `time.sleep(0.01)` call in hot path harms performance.",
    "line": 46,
    "suggestion": "Remove the sleep call."
  },
  {
    "rule_id": "type-checking",
    "severity": "warning",
    "message": "Prefer `isinstance` over `type` for type checking (less error-prone).",
    "line": 57,
    "suggestion": "Replace `type(item) == int` with `isinstance(item, int)`."
  },
  {
    "rule_id": "shadow-built-in",
    "severity": "warning",
    "message": "Variable name `sum` shadows the built-in function. Avoid shadowing built-in names.",
    "line": 95,
    "suggestion": "Rename to avoid shadowing (e.g., `total_sum`)."
  },
  {
    "rule_id": "redundant-conversion",
    "severity": "warning",
    "message": "Unnecessary conversion: `float(str(sum))` is redundant and may cause precision loss.",
    "line": 97,
    "suggestion": "Return `sum` directly instead of converting to string and back."
  }
]