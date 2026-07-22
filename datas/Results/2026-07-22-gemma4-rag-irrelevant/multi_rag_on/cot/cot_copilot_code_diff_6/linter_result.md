```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'functionThatDoesTooMuchAndIsHardToUnderstand' uses camelCase; Python convention (PEP 8) prescribes snake_case for functions.",
    "line": 6,
    "suggestion": "Rename to 'process_requests' or a similar descriptive snake_case name."
  },
  {
    "rule_id": "unnecessary-global",
    "severity": "info",
    "message": "The 'global GLOBAL_SESSION' declaration is unnecessary as the session object is being accessed, not reassigned.",
    "line": 7,
    "suggestion": "Remove the 'global' keyword."
  },
  {
    "rule_id": "broad-exception",
    "severity": "warning",
    "message": "Catching a generic 'Exception' can hide unexpected bugs and makes debugging difficult.",
    "line": 12,
    "suggestion": "Catch specific exceptions such as 'requests.exceptions.RequestException'."
  },
  {
    "rule_id": "bare-except",
    "severity": "error",
    "message": "Bare 'except:' clauses catch all exceptions, including SystemExit and KeyboardInterrupt, which is dangerous.",
    "line": 22,
    "suggestion": "Use 'except Exception:' or, preferably, a specific exception type."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 'weirdVariableName' uses camelCase and is not descriptive of the data it holds.",
    "line": 25,
    "suggestion": "Rename to 'post_response' using snake_case."
  },
  {
    "rule_id": "software-engineering-standards",
    "severity": "warning",
    "message": "The function violates the Single Responsibility Principle by performing multiple unrelated HTTP requests and printing results directly.",
    "line": 6,
    "suggestion": "Split the function into smaller, modular functions (e.g., 'fetch_post', 'list_posts', 'create_post')."
  }
]
```