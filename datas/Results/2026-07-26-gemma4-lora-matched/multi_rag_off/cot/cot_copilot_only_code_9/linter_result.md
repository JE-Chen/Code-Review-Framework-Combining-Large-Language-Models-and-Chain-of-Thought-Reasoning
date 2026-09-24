```json
[
  {
    "rule_id": "duplicate-code",
    "severity": "warning",
    "message": "Functions get_users, get_posts, and get_comments share identical logic and structure, differing only by the endpoint path.",
    "line": 7,
    "suggestion": "Refactor into a single generic function, e.g., `fetch_data(endpoint)`, to reduce duplication."
  },
  {
    "rule_id": "generic-exception-handling",
    "severity": "warning",
    "message": "Catching a generic 'Exception' can hide unexpected bugs and makes debugging difficult.",
    "line": 11,
    "suggestion": "Catch specific exceptions such as `requests.exceptions.RequestException`."
  },
  {
    "rule_id": "generic-exception-handling",
    "severity": "warning",
    "message": "Catching a generic 'Exception' can hide unexpected bugs and makes debugging difficult.",
    "line": 18,
    "suggestion": "Catch specific exceptions such as `requests.exceptions.RequestException`."
  },
  {
    "rule_id": "generic-exception-handling",
    "severity": "warning",
    "message": "Catching a generic 'Exception' can hide unexpected bugs and makes debugging difficult.",
    "line": 25,
    "suggestion": "Catch specific exceptions such as `requests.exceptions.RequestException`."
  },
  {
    "rule_id": "global-state-mutation",
    "severity": "error",
    "message": "The function process_data modifies the global variable GLOBAL_RESULTS, which hinders testability and modularity.",
    "line": 33,
    "suggestion": "Have process_data return a list of results and pass that list to the main function."
  },
  {
    "rule_id": "naming-convention",
    "severity": "info",
    "message": "Variable names 'u', 'p', and 'c' are not descriptive.",
    "line": 37,
    "suggestion": "Rename to 'user', 'post', and 'comment' respectively."
  },
  {
    "rule_id": "potential-key-error",
    "severity": "error",
    "message": "Accessing p['title'] and c['email'] directly after using .get() for checks is inconsistent and may raise a KeyError if the key is missing.",
    "line": 41,
    "suggestion": "Use the value returned by .get() or ensure the key exists before direct access."
  },
  {
    "rule_id": "potential-key-error",
    "severity": "error",
    "message": "Accessing c['email'] directly after using .get() for checks is inconsistent and may raise a KeyError if the key is missing.",
    "line": 45,
    "suggestion": "Use the value returned by .get() or ensure the key exists before direct access."
  },
  {
    "rule_id": "nested-logic-complexity",
    "severity": "info",
    "message": "Deeply nested if-else blocks in main() reduce readability.",
    "line": 52,
    "suggestion": "Use elif statements to flatten the conditional logic."
  }
]
```