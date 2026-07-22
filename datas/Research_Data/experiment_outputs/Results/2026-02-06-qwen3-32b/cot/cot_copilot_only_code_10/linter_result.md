[
  {
    "rule_id": "global-mutable-state",
    "severity": "warning",
    "message": "Global variable GLOBAL_CACHE is used without clear justification. This violates the principle of least privilege and makes the code harder to test.",
    "line": 7,
    "suggestion": "Avoid global state. Use dependency injection or local variables instead."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "Class APIClient is missing a docstring.",
    "line": 9,
    "suggestion": "Add a docstring explaining the class purpose and usage."
  },
  {
    "rule_id": "broad-exception",
    "severity": "warning",
    "message": "Exception caught is too broad. Catching Exception may hide unexpected errors.",
    "line": 21,
    "suggestion": "Catch specific exceptions or re-raise unexpected ones."
  },
  {
    "rule_id": "duplicate-code",
    "severity": "warning",
    "message": "Function get_users is identical to get_posts and get_todos. This violates DRY.",
    "line": 24,
    "suggestion": "Refactor to use a common function or a loop."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "Function get_users is missing a docstring.",
    "line": 24,
    "suggestion": "Add a docstring describing the function parameters and return value."
  },
  {
    "rule_id": "duplicate-code",
    "severity": "warning",
    "message": "Function get_posts is identical to get_users and get_todos. This violates DRY.",
    "line": 29,
    "suggestion": "Refactor to use a common function or a loop."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "Function get_posts is missing a docstring.",
    "line": 29,
    "suggestion": "Add a docstring describing the function parameters and return value."
  },
  {
    "rule_id": "duplicate-code",
    "severity": "warning",
    "message": "Function get_todos is identical to get_users and get_posts. This violates DRY.",
    "line": 34,
    "suggestion": "Refactor to use a common function or a loop."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "Function get_todos is missing a docstring.",
    "line": 34,
    "suggestion": "Add a docstring describing the function parameters and return value."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "Function process_all is missing a docstring.",
    "line": 39,
    "suggestion": "Add a docstring describing the function parameters and return value."
  },
  {
    "rule_id": "incorrect-iteration",
    "severity": "error",
    "message": "Iterating over a dictionary (if data is an error) instead of a list. This will cause a TypeError when the fetch fails.",
    "line": 46,
    "suggestion": "Check if the data is a list before iterating, or handle errors appropriately."
  },
  {
    "rule_id": "incorrect-iteration",
    "severity": "error",
    "message": "Iterating over a dictionary (if data is an error) instead of a list. This will cause a TypeError when the fetch fails.",
    "line": 50,
    "suggestion": "Check if the data is a list before iterating, or handle errors appropriately."
  },
  {
    "rule_id": "incorrect-iteration",
    "severity": "error",
    "message": "Iterating over a dictionary (if data is an error) instead of a list. This will cause a TypeError when the fetch fails.",
    "line": 54,
    "suggestion": "Check if the data is a list before iterating, or handle errors appropriately."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "Function main is missing a docstring.",
    "line": 60,
    "suggestion": "Add a docstring explaining the main entry point."
  }
]