```json
[
  {
    "rule_id": "broad-exception-catch",
    "severity": "warning",
    "message": "Catching a generic Exception can hide unexpected bugs and make debugging difficult.",
    "line": 18,
    "suggestion": "Catch specific exceptions such as requests.exceptions.RequestException."
  },
  {
    "rule_id": "duplicate-code",
    "severity": "info",
    "message": "The functions get_users, get_posts, and get_todos follow an identical pattern of fetching and caching.",
    "line": 21,
    "suggestion": "Refactor into a single generic function, e.g., get_resource(client, resource_name)."
  },
  {
    "rule_id": "potential-key-error",
    "severity": "error",
    "message": "Accessing p['title'] directly after using p.get('title') in the condition is unsafe if the key is missing.",
    "line": 41,
    "suggestion": "Use p.get('title', 'Unknown') or store the result of the first .get() in a variable."
  },
  {
    "rule_id": "deeply-nested-logic",
    "severity": "info",
    "message": "The nested if-else structure for result counts reduces readability.",
    "line": 56,
    "suggestion": "Use elif statements to flatten the logic."
  }
]
```