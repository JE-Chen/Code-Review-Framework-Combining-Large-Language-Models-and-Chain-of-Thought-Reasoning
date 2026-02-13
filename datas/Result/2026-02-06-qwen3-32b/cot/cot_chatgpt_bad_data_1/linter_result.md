[
  {
    "rule_id": "global-state",
    "severity": "error",
    "message": "Global variables (cache, results) create hidden dependencies and state, making code hard to test and maintain.",
    "line": 5,
    "suggestion": "Replace with function parameters or class instance variables."
  },
  {
    "rule_id": "global-state",
    "severity": "error",
    "message": "Global variables (cache, results) create hidden dependencies and state, making code hard to test and maintain.",
    "line": 6,
    "suggestion": "Replace with function parameters or class instance variables."
  },
  {
    "rule_id": "mutable-default",
    "severity": "warning",
    "message": "Mutable default argument 'items' may lead to unexpected behavior if the list is modified.",
    "line": 8,
    "suggestion": "Use None as the default and initialize the list inside the function."
  },
  {
    "rule_id": "bad-list-comprehension",
    "severity": "warning",
    "message": "List comprehension used for side effect (appending to results) instead of building a collection.",
    "line": 12,
    "suggestion": "Replace with a standard for loop to append to results."
  },
  {
    "rule_id": "unnecessary-sleep",
    "severity": "warning",
    "message": "Sleep inside loop causes unnecessary delay and poor performance.",
    "line": 13,
    "suggestion": "Remove the sleep unless rate limiting is explicitly required."
  },
  {
    "rule_id": "use-eval",
    "severity": "error",
    "message": "Using eval() is a security risk and unnecessary for computing x*x.",
    "line": 27,
    "suggestion": "Replace eval with direct computation: return x * x."
  },
  {
    "rule_id": "cache-key-mismatch",
    "severity": "error",
    "message": "Cache keys are integers, but input to get_user_data is a string, so cache lookup never matches.",
    "line": 33,
    "suggestion": "Ensure cache keys and input types match, or use a different data structure."
  }
]