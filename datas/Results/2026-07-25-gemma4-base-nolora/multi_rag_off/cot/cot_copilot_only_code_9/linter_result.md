```json
[
  {
    "rule_id": "duplicate-code",
    "severity": "warning",
    "message": "Functions 'get_users', 'get_posts', and 'get_comments' share identical logic patterns, differing only by the endpoint path.",
    "line": 7,
    "suggestion": "Create a generic 'fetch_data(endpoint)' helper function to handle the request and exception logic."
  },
  {
    "rule_id": "broad-exception",
    "severity": "warning",
    "message": "Catching the base 'Exception' class is too broad and can hide unexpected bugs (e.g., KeyboardInterrupt or SyntaxError).",
    "line": 11,
    "suggestion": "Catch specific exceptions such as 'requests.exceptions.RequestException'."
  },
  {
    "rule_id": "global-state-mutation",
    "severity": "error",
    "message": "The function 'process_data' modifies the global variable 'GLOBAL_RESULTS', which makes the code harder to test and maintain.",
    "line": 31,
    "suggestion": "Modify 'process_data' to return a list of results and pass that list to the 'main' function."
  },
  {
    "rule_id": "naming-convention",
    "severity": "info",
    "message": "Variable names 'u', 'p', and 'c' are not descriptive.",
    "line": 35,
    "suggestion": "Rename 'u' to 'user', 'p' to 'post', and 'c' to 'comment'."
  },
  {
    "rule_id": "potential-key-error",
    "severity": "error",
    "message": "The code uses '.get()' to check for existence but accesses the dictionary via square brackets 'p[\"title\"]' immediately after, which will raise a KeyError if the key is missing.",
    "line": 38,
    "suggestion": "Use the value returned by '.get()' or ensure the key exists before accessing it via brackets."
  },
  {
    "rule_id": "potential-key-error",
    "severity": "error",
    "message": "The code uses '.get()' to check for existence but accesses the dictionary via square brackets 'c[\"email\"]' immediately after, which will raise a KeyError if the key is missing.",
    "line": 42,
    "suggestion": "Use the value returned by '.get()' or ensure the key exists before accessing it via brackets."
  },
  {
    "rule_id": "nested-if-complexity",
    "severity": "info",
    "message": "Deeply nested if-else blocks in 'main' reduce readability.",
    "line": 51,
    "suggestion": "Use 'elif' statements to flatten the conditional logic."
  }
]
```