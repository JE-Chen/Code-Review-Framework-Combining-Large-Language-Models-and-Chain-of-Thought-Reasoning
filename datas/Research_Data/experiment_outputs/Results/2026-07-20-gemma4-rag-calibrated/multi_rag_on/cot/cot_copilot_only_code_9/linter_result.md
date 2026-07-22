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
    "rule_id": "naming-convention",
    "severity": "info",
    "message": "Variable names 'u', 'p', and 'c' are not descriptive.",
    "line": 33,
    "suggestion": "Rename to 'user', 'post', and 'comment' for better readability."
  },
  {
    "rule_id": "potential-key-error",
    "severity": "error",
    "message": "Accessing p['title'] and c['email'] directly after using .get() for checks is inconsistent and may lead to KeyError if the key is missing.",
    "line": 37,
    "suggestion": "Use the value returned by .get() or ensure the key exists before direct access."
  },
  {
    "rule_id": "potential-key-error",
    "severity": "error",
    "message": "Accessing c['email'] directly after using .get() for checks is inconsistent and may lead to KeyError if the key is missing.",
    "line": 41,
    "suggestion": "Use the value returned by .get() or ensure the key exists before direct access."
  },
  {
    "rule_id": "global-state-usage",
    "severity": "warning",
    "message": "Use of GLOBAL_RESULTS creates hidden dependencies and makes the code harder to test and maintain.",
    "line": 5,
    "suggestion": "Pass results as return values and arguments between functions."
  },
  {
    "rule_id": "nested-logic-complexity",
    "severity": "info",
    "message": "Deeply nested if-else blocks in main() reduce readability.",
    "line": 48,
    "suggestion": "Use elif statements to flatten the logic."
  }
]
```