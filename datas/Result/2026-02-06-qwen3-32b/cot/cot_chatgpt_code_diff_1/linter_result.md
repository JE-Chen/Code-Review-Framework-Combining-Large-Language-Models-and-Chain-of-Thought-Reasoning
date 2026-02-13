[
  {
    "rule_id": "no-global-mutable-state",
    "severity": "warning",
    "message": "Mutable global state used. Prefer dependency injection or encapsulation for better testability and maintainability.",
    "line": 7,
    "suggestion": "Replace global STATE with a class or dependency-injected state object."
  },
  {
    "rule_id": "descriptive-naming",
    "severity": "warning",
    "message": "Function name 'update_everything' is vague and does not reflect dual responsibilities (updating state and returning a result).",
    "line": 14,
    "suggestion": "Split into separate functions: one for state updates and one for input processing."
  },
  {
    "rule_id": "no-unnecessary-delay",
    "severity": "warning",
    "message": "Arbitrary sleep introduced for performance testing. Avoid introducing delays in production code.",
    "line": 30,
    "suggestion": "Remove the sleep or replace with a controlled debugging mechanism."
  },
  {
    "rule_id": "broad-exception-catch",
    "severity": "warning",
    "message": "Catching all exceptions (Exception) is dangerous and masks potential errors.",
    "line": 20,
    "suggestion": "Catch specific exceptions or re-raise unexpected errors."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "Function lacks a docstring for documentation and clarity.",
    "line": 14,
    "suggestion": "Add a docstring explaining the function's purpose and parameters."
  },
  {
    "rule_id": "debug-mode-on",
    "severity": "error",
    "message": "Debug mode enabled in production. This exposes sensitive information and should be disabled.",
    "line": 52,
    "suggestion": "Set debug=False in production deployments."
  }
]