```json
[
  {
    "rule_id": "duplicate-code",
    "severity": "warning",
    "message": "Functions get_users, get_posts, and get_comments share identical logic for making requests and handling exceptions.",
    "line": 7,
    "suggestion": "Create a generic helper function (e.g., _fetch_data(endpoint)) to handle the request and try-except block."
  },
  {
    "rule_id": "broad-exception",
    "severity": "warning",
    "message": "Catching a generic Exception can hide unexpected bugs and makes debugging difficult.",
    "line": 11,
    "suggestion": "Catch specific exceptions such as requests.exceptions.RequestException."
  },
  {
    "rule_id": "global-state-mutation",
    "severity": "error",
    "message": "The function process_data modifies the global variable GLOBAL_RESULTS, which hinders testability and modularity.",
    "line": 31,
    "suggestion": "Modify process_data to return a list of results and pass that list to the main function."
  },
  {
    "rule_id": "non-descriptive-naming",
    "severity": "info",
    "message": "Variable names 'u', 'p', and 'c' are not descriptive.",
    "line": 36,
    "suggestion": "Rename variables to 'user', 'post', and 'comment' for better readability."
  },
  {
    "rule_id": "potential-key-error",
    "severity": "error",
    "message": "Accessing p['title'] and c['email'] directly after using .get() for the check is inconsistent and can lead to KeyError if the key is missing.",
    "line": 40,
    "suggestion": "Use the value returned by .get() or ensure the key exists before direct access."
  },
  {
    "rule_id": "deeply-nested-logic",
    "severity": "info",
    "message": "The result count logic in main() uses deeply nested if-else statements.",
    "line": 51,
    "suggestion": "Use elif statements to flatten the logic and improve readability."
  }
]
```