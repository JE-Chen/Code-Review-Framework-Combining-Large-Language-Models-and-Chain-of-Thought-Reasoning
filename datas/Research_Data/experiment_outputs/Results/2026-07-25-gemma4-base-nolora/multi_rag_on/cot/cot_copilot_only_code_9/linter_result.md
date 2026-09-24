```json
[
  {
    "rule_id": "duplicate-code",
    "severity": "warning",
    "message": "Functions get_users, get_posts, and get_comments share identical logic patterns. This violates the DRY (Don't Repeat Yourself) principle.",
    "line": 7,
    "suggestion": "Create a generic helper function (e.g., _fetch_data(endpoint)) to handle the request and exception logic."
  },
  {
    "rule_id": "broad-exception",
    "severity": "warning",
    "message": "Catching the base 'Exception' class is too broad and can hide unexpected bugs (e.g., KeyboardInterrupt or MemoryError).",
    "line": 11,
    "suggestion": "Catch specific exceptions such as requests.exceptions.RequestException."
  },
  {
    "rule_id": "global-state-mutation",
    "severity": "error",
    "message": "The function process_data modifies the global variable GLOBAL_RESULTS, making the code harder to test and maintain.",
    "line": 31,
    "suggestion": "Refactor process_data to return a list of results and pass that list to the main function."
  },
  {
    "rule_id": "non-descriptive-naming",
    "severity": "info",
    "message": "Variable names 'u', 'p', and 'c' are not descriptive.",
    "line": 35,
    "suggestion": "Rename variables to 'user', 'post', and 'comment' for better semantic clarity."
  },
  {
    "rule_id": "potential-key-error",
    "severity": "warning",
    "message": "The code uses .get() to check for existence but then accesses the key directly via bracket notation (e.g., p['title']), which will raise a KeyError if the key is missing.",
    "line": 38,
    "suggestion": "Use the value returned by .get() or ensure the key exists before accessing it via brackets."
  },
  {
    "rule_id": "deeply-nested-logic",
    "severity": "info",
    "message": "The result reporting logic in main() uses deeply nested if-else statements, reducing readability.",
    "line": 50,
    "suggestion": "Use elif statements to flatten the conditional structure."
  }
]
```