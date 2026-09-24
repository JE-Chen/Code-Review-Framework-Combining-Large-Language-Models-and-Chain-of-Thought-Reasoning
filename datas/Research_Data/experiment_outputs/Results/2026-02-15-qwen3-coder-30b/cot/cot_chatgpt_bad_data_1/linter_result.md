[
  {
    "rule_id": "mutable-default-arg",
    "severity": "error",
    "message": "Default argument 'items' uses a mutable type (list). This can lead to unexpected behavior due to shared state across function calls.",
    "line": 6,
    "suggestion": "Use None as default and create a new list inside the function body."
  },
  {
    "rule_id": "global-state-mutation",
    "severity": "warning",
    "message": "Function modifies global variable 'cache', which makes the function non-deterministic and harder to reason about.",
    "line": 9,
    "suggestion": "Pass 'cache' as a parameter or use a class-based approach to manage state."
  },
  {
    "rule_id": "global-state-mutation",
    "severity": "warning",
    "message": "Function modifies global variable 'results', leading to side effects and reduced testability.",
    "line": 10,
    "suggestion": "Return computed values instead of appending to a global list."
  },
  {
    "rule_id": "avoid-eval",
    "severity": "error",
    "message": "Usage of 'eval' can introduce security vulnerabilities and is generally discouraged.",
    "line": 22,
    "suggestion": "Replace with direct arithmetic operation like 'x * x'."
  },
  {
    "rule_id": "unreachable-code",
    "severity": "warning",
    "message": "The second call to 'process_items' has no arguments, so it will operate on an empty list.",
    "line": 17,
    "suggestion": "Ensure that all function calls pass expected parameters."
  },
  {
    "rule_id": "inconsistent-return-types",
    "severity": "warning",
    "message": "The function 'expensive_compute' returns inconsistent types (None, string, int), making its usage unpredictable.",
    "line": 22,
    "suggestion": "Standardize return types or document the exceptions clearly."
  },
  {
    "rule_id": "implicit-list-append",
    "severity": "warning",
    "message": "Using list comprehension syntax for side effect (appending to results) reduces readability.",
    "line": 10,
    "suggestion": "Use explicit append instead of list comprehension."
  },
  {
    "rule_id": "unused-function",
    "severity": "info",
    "message": "Function 'get_user_data' is defined but never used in the current scope.",
    "line": 13,
    "suggestion": "Remove unused functions to reduce clutter."
  }
]