```json
[
  {
    "rule_id": "generic-exception-handling",
    "severity": "warning",
    "message": "Catching a broad 'Exception' can hide unexpected bugs and make debugging difficult.",
    "line": 19,
    "suggestion": "Catch specific exceptions such as requests.exceptions.RequestException."
  },
  {
    "rule_id": "code-duplication",
    "severity": "info",
    "message": "Functions 'get_users', 'get_posts', and 'get_todos' share identical logic patterns.",
    "line": 22,
    "suggestion": "Refactor into a single generic function: fetch_and_cache(client, endpoint, cache_key)."
  },
  {
    "rule_id": "naming-convention",
    "severity": "info",
    "message": "Variable name 'u', 'p', and 't' are not descriptive.",
    "line": 41,
    "suggestion": "Use 'user', 'post', and 'todo' instead."
  },
  {
    "rule_id": "potential-key-error",
    "severity": "error",
    "message": "Accessing 'p[\"title\"]' directly after using '.get()' for the same key is inconsistent and may raise a KeyError if the key is missing.",
    "line": 45,
    "suggestion": "Use 'p.get(\"title\", \"\")' or ensure the key exists before direct access."
  },
  {
    "rule_id": "cognitive-complexity",
    "severity": "info",
    "message": "Deeply nested if-else structure reduces readability.",
    "line": 60,
    "suggestion": "Use an 'if-elif-else' chain to flatten the logic."
  }
]
```