[
  {
    "rule_id": "no-global-state",
    "severity": "warning",
    "message": "Global variable GLOBAL_RESULTS violates modularity and testability by creating implicit state dependencies.",
    "line": 5,
    "suggestion": "Replace global state with function return values and explicit parameters."
  },
  {
    "rule_id": "no-duplicate-code",
    "severity": "warning",
    "message": "Identical HTTP request logic in get_users, get_posts, and get_comments indicates code duplication.",
    "line": 9,
    "suggestion": "Extract common request logic into a reusable helper function."
  },
  {
    "rule_id": "no-broad-exception",
    "severity": "warning",
    "message": "Catching Exception is too broad and may mask unexpected errors like SyntaxError or KeyboardInterrupt.",
    "line": 11,
    "suggestion": "Catch specific exceptions (e.g., requests.exceptions.RequestException)."
  },
  {
    "rule_id": "no-docstrings",
    "severity": "info",
    "message": "Functions lack descriptive docstrings explaining purpose, parameters, and return values.",
    "line": 7,
    "suggestion": "Add docstrings to all public functions for clarity and documentation."
  },
  {
    "rule_id": "no-tests",
    "severity": "info",
    "message": "No unit or integration tests exist to verify functionality correctness.",
    "line": 35,
    "suggestion": "Implement unit tests for core logic (e.g., data processing and edge cases)."
  }
]