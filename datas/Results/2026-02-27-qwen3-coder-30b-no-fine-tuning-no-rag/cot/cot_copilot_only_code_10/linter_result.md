```json
[
  {
    "rule_id": "no-global-variables",
    "severity": "warning",
    "message": "Usage of global variable 'GLOBAL_CACHE' may lead to unexpected side effects and reduce testability.",
    "line": 8,
    "suggestion": "Pass cache as a parameter or use a singleton pattern with explicit state management."
  },
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Variable 'r' in the main loop is unused; it's only used for printing but could be replaced by direct iteration.",
    "line": 49,
    "suggestion": "Use direct iteration over results without assigning to 'r'."
  },
  {
    "rule_id": "no-duplicate-code",
    "severity": "warning",
    "message": "Functions 'get_users', 'get_posts', and 'get_todos' share nearly identical logic and can be refactored into a single generic function.",
    "line": 22,
    "suggestion": "Refactor into a common helper that accepts endpoint as a parameter."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic numbers 5 and 20 are used directly in conditional statements. These should be extracted into named constants for clarity.",
    "line": 52,
    "suggestion": "Define constants like MIN_RESULTS_THRESHOLD = 5 and MAX_RESULTS_THRESHOLD = 20 for better readability."
  },
  {
    "rule_id": "no-bad-exception-handling",
    "severity": "warning",
    "message": "Catching all exceptions ('Exception') is too broad and may mask unexpected errors. Consider catching specific exceptions.",
    "line": 17,
    "suggestion": "Catch specific exceptions such as requests.RequestException or ConnectionError instead of general Exception."
  },
  {
    "rule_id": "no-unexpected-side-effects",
    "severity": "warning",
    "message": "The 'fetch' method modifies the global cache directly, which introduces hidden side effects and makes testing difficult.",
    "line": 25,
    "suggestion": "Avoid modifying global state inside methods; pass cache as an argument or encapsulate caching behavior separately."
  }
]
```