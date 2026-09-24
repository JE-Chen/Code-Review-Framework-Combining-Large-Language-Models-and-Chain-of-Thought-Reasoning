```json
[
  {
    "rule_id": "duplicate-code",
    "severity": "warning",
    "message": "The functions get_users, get_posts, and get_todos share identical logic and only differ by the endpoint string.",
    "line": 24,
    "suggestion": "Refactor into a single generic function, e.g., `fetch_and_cache(client, endpoint, cache_key)`."
  },
  {
    "rule_id": "naming-convention",
    "severity": "info",
    "message": "Variable name 'u', 'p', and 't' are not descriptive.",
    "line": 41,
    "suggestion": "Rename to 'user', 'post', and 'todo' respectively for better readability."
  },
  {
    "rule_id": "potential-bug",
    "severity": "error",
    "message": "The code attempts to iterate over 'users', 'posts', and 'todos' without verifying if the API call returned a list or an error dictionary.",
    "line": 41,
    "suggestion": "Check if the returned data is a list before iterating, or handle the error dictionary returned by APIClient.fetch."
  },
  {
    "rule_id": "potential-bug",
    "severity": "error",
    "message": "Direct access to p['title'] may raise a KeyError if the key is missing, whereas other accesses use .get().",
    "line": 45,
    "suggestion": "Use p.get('title', 'Unknown') for consistency and safety."
  },
  {
    "rule_id": "software-engineering-standard",
    "severity": "warning",
    "message": "Deeply nested if-else blocks reduce readability.",
    "line": 61,
    "suggestion": "Use a flatter structure or a mapping/lookup table to categorize the result counts."
  }
]
```