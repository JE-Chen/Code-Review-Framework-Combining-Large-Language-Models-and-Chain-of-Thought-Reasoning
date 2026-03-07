[
  {
    "rule_id": "mutable-default-argument",
    "severity": "error",
    "message": "Mutable default argument 'container' used in function 'add_item'. Default arguments are evaluated once at function definition time.",
    "line": 2,
    "suggestion": "Use None as default and create a new list inside the function body."
  },
  {
    "rule_id": "global-state-mutation",
    "severity": "error",
    "message": "Function 'append_global' modifies a global list, which introduces hidden coupling and makes behavior hard to reason about.",
    "line": 7,
    "suggestion": "Pass the list as a parameter or encapsulate the state in a class."
  },
  {
    "rule_id": "input-mutation",
    "severity": "error",
    "message": "Function 'mutate_input' modifies its input argument directly, which can lead to unexpected side effects for callers.",
    "line": 11,
    "suggestion": "Return a new list instead of mutating the input."
  },
  {
    "rule_id": "nested-conditionals",
    "severity": "warning",
    "message": "Deeply nested conditional logic in 'nested_conditions' reduces readability and increases complexity.",
    "line": 16,
    "suggestion": "Refactor using early returns or helper functions to flatten conditionals."
  },
  {
    "rule_id": "broad-exception",
    "severity": "warning",
    "message": "Catching generic 'Exception' in 'risky_division' may mask unexpected errors.",
    "line": 27,
    "suggestion": "Catch specific exceptions or re-raise after logging."
  },
  {
    "rule_id": "inconsistent-return-type",
    "severity": "error",
    "message": "Function 'inconsistent_return' returns different types ('int' and 'str') based on conditional branches.",
    "line": 32,
    "suggestion": "Ensure consistent return type across all branches."
  },
  {
    "rule_id": "side-effect-in-comprehension",
    "severity": "error",
    "message": "List comprehension contains a side effect (print), violating the principle that comprehensions should be for building collections.",
    "line": 37,
    "suggestion": "Replace with an explicit loop for side effects."
  },
  {
    "rule_id": "unsafe-eval",
    "severity": "error",
    "message": "Function 'run_code' uses 'eval', which introduces security vulnerabilities.",
    "line": 42,
    "suggestion": "Avoid dynamic code execution unless absolutely necessary and validate inputs thoroughly."
  }
]