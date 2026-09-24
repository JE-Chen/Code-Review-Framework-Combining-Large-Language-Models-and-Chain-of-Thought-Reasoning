```json
[
  {
    "rule_id": "duplicate-code",
    "severity": "warning",
    "message": "Functions 'get_users', 'get_posts', and 'get_todos' contain nearly identical logic for fetching and caching data.",
    "line": 24,
    "suggestion": "Create a generic 'get_resource(client, resource_name)' function to handle the fetch and cache logic."
  },
  {
    "rule_id": "broad-exception",
    "severity": "warning",
    "message": "Catching the base 'Exception' class can hide unexpected bugs and makes debugging difficult.",
    "line": 19,
    "suggestion": "Catch specific exceptions such as 'requests.exceptions.RequestException'."
  },
  {
    "rule_id": "potential-key-error",
    "severity": "error",
    "message": "Accessing 'p[\"title\"]' directly after using '.get()' for the same key is inconsistent and may cause a KeyError if the key is missing.",
    "line": 42,
    "suggestion": "Use 'p.get(\"title\", \"\")' or store the result of the first '.get()' in a variable."
  },
  {
    "rule_id": "nested-conditionals",
    "severity": "info",
    "message": "Deeply nested if-else blocks reduce readability.",
    "line": 56,
    "suggestion": "Use 'elif' statements to flatten the logic for checking the length of 'results'."
  },
  {
    "rule_id": "global-state-mutation",
    "severity": "warning",
    "message": "Directly mutating 'GLOBAL_CACHE' inside data-fetching functions makes the code harder to test and reason about.",
    "line": 26,
    "suggestion": "Pass a cache object as an argument or encapsulate the cache within the 'APIClient' class."
  }
]
```