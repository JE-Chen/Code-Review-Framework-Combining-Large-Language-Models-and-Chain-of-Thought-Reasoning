```json
[
  {
    "rule_id": "missing-docstrings",
    "severity": "error",
    "message": "Functions and classes lack docstrings.",
    "line": 1,
    "suggestion": "Add docstrings to functions and classes for clarity."
  },
  {
    "rule_id": "code-duplication",
    "severity": "warning",
    "message": "get_users(), get_posts(), get_comments() share identical logic.",
    "line": 1,
    "suggestion": "Refactor into a shared function for request handling."
  },
  {
    "rule_id": "improper-error-handling",
    "severity": "warning",
    "message": "Error messages are printed but not returned or logged consistently.",
    "line": 1,
    "suggestion": "Return error codes or log exceptions with context."
  },
  {
    "rule_id": "inconsistent-logic",
    "severity": "warning",
    "message": "Conditionals in process_data() are not generalized.",
    "line": 1,
    "suggestion": "Create helper functions for data validation."
  },
  {
    "rule_id": "inefficient-output",
    "severity": "warning",
    "message": "Main() prints results with conditional checks that are not reused.",
    "line": 1,
    "suggestion": "Refactor output formatting into a helper function."
  }
]
```