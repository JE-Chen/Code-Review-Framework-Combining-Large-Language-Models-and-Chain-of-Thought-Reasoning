[
  {
    "rule_id": "no-global-variables",
    "severity": "error",
    "message": "Usage of global variables (GLOBAL_THING, STRANGE_CACHE) introduces hidden coupling and makes behavior hard to reason about.",
    "line": 10,
    "suggestion": "Pass state explicitly or encapsulate it in a class."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '37' used directly; consider extracting to a named constant.",
    "line": 12,
    "suggestion": "Define MAGIC as a descriptive constant like MAX_ITERATIONS or OFFSET_CONSTANT."
  },
  {
    "rule_id": "no-dangerous-defaults",
    "severity": "error",
    "message": "Mutable default argument 'y=[]' can cause unexpected behavior due to shared state.",
    "line": 14,
    "suggestion": "Use None as default and initialize list inside function body."
  },
  {
    "rule_id": "no-dangerous-defaults",
    "severity": "error",
    "message": "Mutable default argument 'z={\"a\": 1}' can cause unexpected behavior due to shared state.",
    "line": 14,
    "suggestion": "Use None as default and initialize dict inside function body."
  },
  {
    "rule_id": "no-unnecessary-loop",
    "severity": "warning",
    "message": "Unnecessary loop over range(len(df)) used instead of vectorized operations.",
    "line": 49,
    "suggestion": "Use vectorized operations or pandas apply/agg where possible."
  },
  {
    "rule_id": "no-broad-exception",
    "severity": "error",
    "message": "Empty except block catches all exceptions without logging or re-raising.",
    "line": 32,
    "suggestion": "Log the exception or re-raise it after handling specific cases."
  },
  {
    "rule_id": "no-broad-exception",
    "severity": "error",
    "message": "Empty except block catches all exceptions without logging or re-raising.",
    "line": 61,
    "suggestion": "Log the exception or re-raising it after handling specific cases."
  },
  {
    "rule_id": "no-redundant-calculation",
    "severity": "warning",
    "message": "Repeated computation of df['mystery'] and df['normalized'] inside loops.",
    "line": 49,
    "suggestion": "Compute values once and store them in variables before looping."
  },
  {
    "rule_id": "no-unexpected-side-effects",
    "severity": "error",
    "message": "Function modifies global variable GLOBAL_THING which may surprise callers.",
    "line": 27,
    "suggestion": "Avoid modifying external state; return modified values explicitly."
  },
  {
    "rule_id": "no-inconsistent-return-types",
    "severity": "warning",
    "message": "Return type varies based on conditional logic; unclear what's returned.",
    "line": 67,
    "suggestion": "Ensure consistent return types throughout function."
  },
  {
    "rule_id": "no-complex-nested-logic",
    "severity": "warning",
    "message": "Complex nested logic with multiple conditionals and exception handling increases cognitive load.",
    "line": 53,
    "suggestion": "Break down into smaller helper functions for clarity."
  }
]