```json
[
  {
    "rule_id": "duplicate-code",
    "severity": "warning",
    "message": "Functions 'get_users', 'get_posts', and 'get_comments' share identical logic for making requests and handling exceptions.",
    "line": 7,
    "suggestion": "Create a generic 'fetch_data(endpoint)' helper function to reduce duplication."
  },
  {
    "rule_id": "broad-exception",
    "severity": "warning",
    "message": "Catching the base 'Exception' class is too broad and can hide unexpected bugs.",
    "line": 11,
    "suggestion": "Catch specific exceptions such as 'requests.exceptions.RequestException'."
  },
  {
    "rule_id": "broad-exception",
    "severity": "warning",
    "message": "Catching the base 'Exception' class is too broad and can hide unexpected bugs.",
    "line": 18,
    "suggestion": "Catch specific exceptions such as 'requests.exceptions.RequestException'."
  },
  {
    "rule_id": "broad-exception",
    "severity": "warning",
    "message": "Catching the base 'Exception' class is too broad and can hide unexpected bugs.",
    "line": 25,
    "suggestion": "Catch specific exceptions such as 'requests.exceptions.RequestException'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "info",
    "message": "Variable names 'u', 'p', and 'c' are not descriptive.",
    "line": 33,
    "suggestion": "Rename to 'user', 'post', and 'comment' respectively."
  },
  {
    "rule_id": "potential-key-error",
    "severity": "error",
    "message": "Accessing 'p[\"title\"]' and 'c[\"email\"]' directly after using '.get()' for the check is inconsistent and may cause a KeyError if the key is missing.",
    "line": 37,
    "suggestion": "Use the value returned by '.get()' or ensure the key exists before direct access."
  },
  {
    "rule_id": "potential-key-error",
    "severity": "error",
    "message": "Accessing 'c[\"email\"]' directly after using '.get()' for the check is inconsistent and may cause a KeyError if the key is missing.",
    "line": 41,
    "suggestion": "Use the value returned by '.get()' or ensure the key exists before direct access."
  },
  {
    "rule_id": "global-state-mutation",
    "severity": "warning",
    "message": "The function 'process_data' modifies the global variable 'GLOBAL_RESULTS', making the code harder to test and maintain.",
    "line": 33,
    "suggestion": "Have 'process_data' return a list of results and pass that list to 'main'."
  },
  {
    "rule_id": "nested-logic",
    "severity": "info",
    "message": "Deeply nested if-else blocks reduce readability.",
    "line": 48,
    "suggestion": "Use 'elif' statements to flatten the conditional logic."
  }
]
```