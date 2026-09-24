```json
[
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "Use of shared mutable state at the module level (GLOBAL_SESSION) can introduce hidden coupling and make testing difficult.",
    "line": 3,
    "suggestion": "Pass the session explicitly as a function argument or encapsulate it within a class."
  },
  {
    "rule_id": "naming-convention",
    "severity": "info",
    "message": "Function name 'functionThatDoesTooMuchAndIsHardToUnderstand' does not follow Python's snake_case naming convention.",
    "line": 6,
    "suggestion": "Rename to 'fetch_and_post_data' or a similar descriptive snake_case name."
  },
  {
    "rule_id": "single-responsibility",
    "severity": "warning",
    "message": "The function performs multiple unrelated tasks: fetching a single post, fetching all posts, and creating a post.",
    "line": 6,
    "suggestion": "Split the logic into smaller, focused functions (e.g., 'get_post', 'get_all_posts', 'create_post')."
  },
  {
    "rule_id": "broad-exception",
    "severity": "error",
    "message": "Catching a broad exception 'Exception' can hide real bugs and make debugging difficult.",
    "line": 12,
    "suggestion": "Catch specific exceptions such as 'requests.exceptions.RequestException'."
  },
  {
    "rule_id": "broad-exception",
    "severity": "error",
    "message": "Bare 'except:' clause catches all exceptions, including SystemExit and KeyboardInterrupt.",
    "line": 22,
    "suggestion": "Catch specific exceptions or at least 'Exception'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "info",
    "message": "Variable name 'weirdVariableName' is not descriptive and does not follow snake_case convention.",
    "line": 25,
    "suggestion": "Rename to 'post_response'."
  }
]
```