[
  {
    "rule_id": "mutable-default-arg",
    "severity": "error",
    "message": "Mutable default arguments for parameters y and z may cause unexpected behavior across function calls.",
    "line": 15,
    "suggestion": "Use None as default and initialize inside function."
  },
  {
    "rule_id": "unused-parameter",
    "severity": "warning",
    "message": "Parameter y is defined but never used.",
    "line": 15,
    "suggestion": "Remove unused parameter y."
  },
  {
    "rule_id": "unused-parameter",
    "severity": "warning",
    "message": "Parameter z is defined but never used.",
    "line": 15,
    "suggestion": "Remove unused parameter z."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "warning",
    "message": "Function lacks a docstring explaining purpose, parameters, and return values.",
    "line": 15,
    "suggestion": "Add a docstring."
  },
  {
    "rule_id": "single-responsibility",
    "severity": "warning",
    "message": "Function does too many unrelated things: data generation, transformation, plotting, and side effects.",
    "line": 15,
    "suggestion": "Split function into smaller, focused functions."
  },
  {
    "rule_id": "side-effect",
    "severity": "error",
    "message": "Function has side effects (plotting and modifying global state) which make it non-pure and hard to test.",
    "line": 15,
    "suggestion": "Separate side effects into dedicated functions."
  },
  {
    "rule_id": "magic-number",
    "severity": "warning",
    "message": "Magic number 37 used without explanation. Consider defining a named constant.",
    "line": 12,
    "suggestion": "Replace with a descriptive constant name."
  },
  {
    "rule_id": "global-mutable-state",
    "severity": "error",
    "message": "Modifying global variable GLOBAL_THING introduces hidden coupling and makes code harder to test.",
    "line": 24,
    "suggestion": "Remove global state and return the necessary data."
  },
  {
    "rule_id": "global-mutable-state",
    "severity": "error",
    "message": "Mutating module-level cache STRANGE_CACHE introduces hidden coupling and state across calls.",
    "line": 48,
    "suggestion": "Remove global cache and handle state internally."
  },
  {
    "rule_id": "inefficient-loop",
    "severity": "warning",
    "message": "Loop over DataFrame using iloc is inefficient and error-prone; use vectorized operations instead.",
    "line": 39,
    "suggestion": "Replace loop with vectorized operations."
  },
  {
    "rule_id": "broad-exception",
    "severity": "warning",
    "message": "Catching Exception generally hides bugs; catch specific exceptions instead.",
    "line": 40,
    "suggestion": "Replace with specific exception handling or remove the try-except."
  },
  {
    "rule_id": "broad-exception",
    "severity": "warning",
    "message": "Catching Exception generally hides bugs; catch specific exceptions instead.",
    "line": 55,
    "suggestion": "Replace with specific exception handling or remove the try-except."
  },
  {
    "rule_id": "unnecessary-sleep",
    "severity": "warning",
    "message": "Unnecessary time.sleep calls slow down execution without purpose.",
    "line": 58,
    "suggestion": "Remove the sleep calls."
  },
  {
    "rule_id": "unnecessary-work",
    "severity": "warning",
    "message": "Summary includes 'something_useless' which is a fixed sum and not meaningful.",
    "line": 47,
    "suggestion": "Remove the useless field."
  }
]