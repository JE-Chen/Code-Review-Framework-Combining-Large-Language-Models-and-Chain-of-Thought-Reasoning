[
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Variable 'txtAge' is defined but not used in the scope.",
    "line": 25,
    "suggestion": "Remove unused variable or use it appropriately."
  },
  {
    "rule_id": "no-implicit-any",
    "severity": "error",
    "message": "Implicit any type used in function parameters or return types.",
    "line": 48,
    "suggestion": "Explicitly define parameter and return types where possible."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '1000' found in timer start call. Consider defining as a named constant.",
    "line": 57,
    "suggestion": "Define '1000' as a constant like `UPDATE_INTERVAL_MS = 1000`."
  },
  {
    "rule_id": "no-duplicate-code",
    "severity": "warning",
    "message": "Similar logic exists in both add_user and delete_user functions for updating UI status.",
    "line": 49,
    "suggestion": "Extract common UI update logic into a helper method."
  },
  {
    "rule_id": "no-global-state",
    "severity": "info",
    "message": "Global app instance is created at module level which may reduce testability.",
    "line": 10,
    "suggestion": "Pass app instance as dependency or encapsulate in a factory."
  },
  {
    "rule_id": "no-unhandled-exceptions",
    "severity": "error",
    "message": "Exception handling catches all exceptions without specific logging or re-raising.",
    "line": 42,
    "suggestion": "Catch specific exceptions instead of bare except clause."
  },
  {
    "rule_id": "no-side-effects",
    "severity": "warning",
    "message": "Function 'add_user' has side effects including sleep and modifying global state.",
    "line": 39,
    "suggestion": "Avoid side effects within core logic; move blocking operations to background threads."
  }
]