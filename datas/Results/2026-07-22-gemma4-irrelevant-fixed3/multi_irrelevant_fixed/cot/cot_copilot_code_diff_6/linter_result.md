```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'functionThatDoesTooMuchAndIsHardToUnderstand' uses camelCase. Python convention (PEP 8) prescribes snake_case for functions.",
    "line": 7,
    "suggestion": "Rename to 'function_that_does_too_much_and_is_hard_to_understand' or a more descriptive, concise name."
  },
  {
    "rule_id": "unnecessary-global",
    "severity": "info",
    "message": "The 'global GLOBAL_SESSION' declaration is unnecessary as the session object is being accessed, not reassigned.",
    "line": 8,
    "suggestion": "Remove the 'global' keyword."
  },
  {
    "rule_id": "broad-exception",
    "severity": "warning",
    "message": "Catching a generic 'Exception' can hide unexpected bugs and makes debugging difficult.",
    "line": 13,
    "suggestion": "Catch specific exceptions, such as 'requests.exceptions.RequestException'."
  },
  {
    "rule_id": "bare-except",
    "severity": "error",
    "message": "Bare 'except:' clauses catch all exceptions, including SystemExit and KeyboardInterrupt, which is generally discouraged.",
    "line": 23,
    "suggestion": "Use 'except Exception:' or, preferably, a specific exception type."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 'weirdVariableName' uses camelCase and is not descriptive of the data it holds.",
    "line": 26,
    "suggestion": "Rename to 'response' or 'post_response' using snake_case."
  },
  {
    "rule_id": "software-engineering-standards",
    "severity": "warning",
    "message": "The function performs multiple unrelated network requests and print operations, violating the Single Responsibility Principle.",
    "line": 7,
    "suggestion": "Split the function into smaller, modular functions (e.g., one for GET requests and one for POST requests)."
  }
]
```