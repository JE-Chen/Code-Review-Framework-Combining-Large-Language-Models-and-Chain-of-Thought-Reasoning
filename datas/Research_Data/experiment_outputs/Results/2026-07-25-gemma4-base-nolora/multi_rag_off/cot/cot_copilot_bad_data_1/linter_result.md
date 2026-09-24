```json
[
  {
    "rule_id": "mutable-default-argument",
    "severity": "error",
    "message": "Using a mutable default argument (list) can lead to unexpected behavior as the list is shared across all function calls.",
    "line": 1,
    "suggestion": "Use 'container=None' and initialize it inside the function: 'if container is None: container = []'."
  },
  {
    "rule_id": "deeply-nested-conditions",
    "severity": "warning",
    "message": "Excessive nesting of conditional statements reduces readability and maintainability.",
    "line": 20,
    "suggestion": "Flatten the logic using guard clauses or combined boolean expressions (e.g., 'if 0 < x < 10 and x % 2 == 0')."
  },
  {
    "rule_id": "broad-exception-catch",
    "severity": "warning",
    "message": "Catching a generic 'Exception' can hide unexpected errors (e.g., KeyboardInterrupt or SystemExit) and makes debugging difficult.",
    "line": 38,
    "suggestion": "Catch the specific exception expected, such as 'ZeroDivisionError' or 'TypeError'."
  },
  {
    "rule_id": "inconsistent-return-types",
    "severity": "info",
    "message": "The function returns different types (int and str) depending on the input, which may cause type errors in the calling code.",
    "line": 42,
    "suggestion": "Ensure the function returns a consistent type or use type hinting to explicitly define the union return type."
  },
  {
    "rule_id": "side-effect-in-comprehension",
    "severity": "warning",
    "message": "List comprehensions should be used for creating lists, not for executing side effects like 'print()'.",
    "line": 54,
    "suggestion": "Use a standard 'for' loop for printing."
  },
  {
    "rule_id": "security-eval",
    "severity": "error",
    "message": "The use of 'eval()' is a critical security risk as it allows the execution of arbitrary code from a string.",
    "line": 60,
    "suggestion": "Avoid 'eval()'. Use 'ast.literal_eval()' for safe evaluation of literals or implement a specific parser."
  }
]
```