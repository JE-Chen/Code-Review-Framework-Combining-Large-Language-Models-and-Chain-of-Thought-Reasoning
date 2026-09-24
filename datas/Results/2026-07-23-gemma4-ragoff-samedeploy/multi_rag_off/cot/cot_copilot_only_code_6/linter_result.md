```json
[
  {
    "rule_id": "global-state-mutation",
    "severity": "warning",
    "message": "Use of 'global' keyword to modify state (USER_COUNT, DATA_STORE) makes the application non-thread-safe and difficult to test.",
    "line": 15,
    "suggestion": "Use a database or a thread-safe state management object."
  },
  {
    "rule_id": "generic-exception-handling",
    "severity": "error",
    "message": "Catching a generic 'Exception' can hide unexpected bugs and provides poor error granularity.",
    "line": 21,
    "suggestion": "Catch specific exceptions (e.g., TypeError, KeyError) and handle them accordingly."
  },
  {
    "rule_id": "potential-none-type-error",
    "severity": "error",
    "message": "The code calls len() and .upper() on 'item' without verifying that 'item' is a string. If request.json.get('item') is None or an integer, this will raise an AttributeError/TypeError.",
    "line": 30,
    "suggestion": "Validate that 'item' is a string before performing string operations."
  },
  {
    "rule_id": "deeply-nested-logic",
    "severity": "warning",
    "message": "The 'complex_route' function has excessive nesting (4+ levels), which reduces readability and maintainability.",
    "line": 46,
    "suggestion": "Use guard clauses to flatten the logic and return early."
  },
  {
    "rule_id": "security-debug-mode",
    "severity": "warning",
    "message": "Running Flask with debug=True in a production-like environment can expose sensitive traceback information and allow arbitrary code execution.",
    "line": 65,
    "suggestion": "Set debug=False or use an environment variable to toggle debug mode."
  }
]
```