```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'functionThatDoesTooMuchAndIsHardToUnderstand' uses camelCase; Python convention (PEP 8) prescribes snake_case for functions.",
    "line": 6,
    "suggestion": "Rename to 'function_that_does_too_much_and_is_hard_to_understand' or a more descriptive, concise name."
  },
  {
    "rule_id": "unnecessary-global",
    "severity": "info",
    "message": "The 'global GLOBAL_SESSION' declaration is unnecessary because the session object is being mutated/accessed, not reassigned.",
    "line": 7,
    "suggestion": "Remove the 'global' keyword."
  },
  {
    "rule_id": "broad-exception",
    "severity": "warning",
    "message": "Catching a generic 'Exception' can hide unexpected bugs and makes debugging difficult.",
    "line": 12,
    "suggestion": "Catch specific exceptions, such as 'requests.exceptions.RequestException'."
  },
  {
    "rule_id": "bare-except",
    "severity": "error",
    "message": "Bare 'except:' clauses catch all exceptions, including SystemExit and KeyboardInterrupt, which is generally discouraged.",
    "line": 22,
    "suggestion": "Use 'except Exception:' or a specific exception class."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 'weirdVariableName' uses camelCase; Python convention (PEP 8) prescribes snake_case for variables.",
    "line": 25,
    "suggestion": "Rename to 'weird_variable_name' or a name that describes the content (e.g., 'post_response')."
  },
  {
    "rule_id": "software-engineering-modularization",
    "severity": "warning",
    "message": "The function performs multiple unrelated network requests (GET and POST) and handles its own printing, violating the Single Responsibility Principle.",
    "line": 6,
    "suggestion": "Split the function into smaller, modular functions (e.g., 'fetch_post', 'create_post')."
  }
]
```