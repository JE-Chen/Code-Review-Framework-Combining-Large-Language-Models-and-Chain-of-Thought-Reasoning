```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'doStuff' does not follow snake_case naming convention.",
    "line": 6,
    "suggestion": "Rename 'doStuff' to 'do_stuff' for consistency with Python naming conventions."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'processEverything' does not follow snake_case naming convention.",
    "line": 30,
    "suggestion": "Rename 'processEverything' to 'process_everything' for consistency with Python naming conventions."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable name 'sum' shadows built-in function 'sum'.",
    "line": 55,
    "suggestion": "Rename 'sum' to avoid shadowing the built-in 'sum' function."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Parameter 'bucket' uses a mutable default argument, which can lead to unexpected behavior.",
    "line": 60,
    "suggestion": "Use 'None' as default and create a new list inside the function body."
  },
  {
    "rule_id": "complexity",
    "severity": "error",
    "message": "Nested conditional statements exceed recommended complexity; consider simplifying logic.",
    "line": 13,
    "suggestion": "Refactor nested if-else blocks into simpler logical structure or extract to helper functions."
  },
  {
    "rule_id": "magic-numbers",
    "severity": "warning",
    "message": "Magic number '3.14159' used multiple times; consider defining as a named constant.",
    "line": 10,
    "suggestion": "Define PI as a constant at module level to improve readability and maintainability."
  },
  {
    "rule_id": "magic-numbers",
    "severity": "warning",
    "message": "Magic number '2.71828' used; consider defining as a named constant.",
    "line": 8,
    "suggestion": "Define E as a constant at module level to improve readability and maintainability."
  },
  {
    "rule_id": "unused-vars",
    "severity": "warning",
    "message": "Unused parameter 'i' and 'j' in function 'doStuff'.",
    "line": 6,
    "suggestion": "Remove unused parameters 'i' and 'j' from the function signature."
  },
  {
    "rule_id": "exception-handling",
    "severity": "error",
    "message": "Catch-all exception handler ('except:') is too broad and may hide unexpected errors.",
    "line": 42,
    "suggestion": "Specify the expected exception type (e.g., ValueError) to catch only intended exceptions."
  },
  {
    "rule_id": "global-state",
    "severity": "warning",
    "message": "Use of global variable 'total_result' makes function non-deterministic and harder to test.",
    "line": 19,
    "suggestion": "Avoid modifying global state; pass required values as parameters or return them explicitly."
  },
  {
    "rule_id": "readability",
    "severity": "warning",
    "message": "Overuse of temporary variables ('temp1', 'temp2') reduces clarity.",
    "line": 25,
    "suggestion": "Simplify assignment by combining operations directly."
  },
  {
    "rule_id": "logic-error",
    "severity": "error",
    "message": "Inconsistent handling of zero division case may cause incorrect behavior.",
    "line": 29,
    "suggestion": "Ensure consistent handling of edge cases like division by zero."
  },
  {
    "rule_id": "performance",
    "severity": "warning",
    "message": "Use of 'time.sleep(0.01)' introduces artificial delay without clear purpose.",
    "line": 23,
    "suggestion": "Remove or justify use of sleep for performance testing or debugging purposes."
  }
]
```