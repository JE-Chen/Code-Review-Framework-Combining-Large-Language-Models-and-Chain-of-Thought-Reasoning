Based on the provided global rules, here is the code review for `bad_requests.py`.

### Summary Report
The code exhibits several critical issues regarding naming conventions, software engineering standards (specifically modularity and exception handling), and overall readability. It follows a "scripting" style rather than a professional software engineering approach.

---

### Detailed Linter Messages

```json
[
  {
    "rule_id": "naming-convention",
    "severity": "error",
    "message": "Function name 'functionThatDoesTooMuchAndIsHardToUnderstand' uses camelCase instead of snake_case (PEP 8).",
    "line": 7,
    "suggestion": "Rename to 'fetch_and_post_data' or similar descriptive snake_case name."
  },
  {
    "rule_id": "modular-design",
    "severity": "warning",
    "message": "The function violates the Single Responsibility Principle by handling multiple distinct network requests and print operations.",
    "line": 7,
    "suggestion": "Split the function into smaller, focused functions (e.g., 'get_single_post', 'get_all_posts', 'create_post')."
  },
  {
    "rule_id": "redundant-global",
    "severity": "info",
    "message": "The 'global GLOBAL_SESSION' declaration is unnecessary as the session is being accessed, not reassigned.",
    "line": 8,
    "suggestion": "Remove the 'global' keyword."
  },
  {
    "rule_id": "exception-handling",
    "severity": "error",
    "message": "Generic 'Exception' catch block provides no specific error handling and suppresses potential critical failures.",
    "line": 13,
    "suggestion": "Catch specific exceptions such as 'requests.exceptions.RequestException'."
  },
  {
    "rule_id": "bare-except",
    "severity": "error",
    "message": "Bare 'except:' clause catches all exceptions, including SystemExit and KeyboardInterrupt, which is dangerous.",
    "line": 23,
    "suggestion": "Specify the exception type or use 'except Exception:'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 'r2' is non-descriptive.",
    "line": 17,
    "suggestion": "Rename to 'posts_response' or 'all_posts'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 'weirdVariableName' is non-descriptive and uses camelCase.",
    "line": 26,
    "suggestion": "Rename to 'create_response' or 'post_result'."
  },
  {
    "rule_id": "security-validation",
    "severity": "warning",
    "message": "The code lacks timeout parameters on requests, which could lead to the program hanging indefinitely.",
    "line": 10,
    "suggestion": "Add a 'timeout' argument to all requests.get() and requests.post() calls."
  },
  {
    "rule_id": "documentation",
    "severity": "info",
    "message": "Missing docstring for the main function and module.",
    "line": 7,
    "suggestion": "Add a triple-quoted string explaining the function's purpose, arguments, and return values."
  }
]
```

### Final Assessment
- **Readability & Consistency**: Poor. Mixing camelCase with snake_case and using non-descriptive names.
- **Software Engineering Standards**: Low. Logic is coupled and hard to test.
- **Logic & Correctness**: Risky. Bare except blocks mask bugs.
- **Performance & Security**: Moderate risk due to missing request timeouts.