```json
[
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "The use of a global `SESSION` object introduces shared mutable state at the module level, which can lead to hidden coupling and make testing difficult.",
    "line": 7,
    "suggestion": "Encapsulate the session within a class or pass it as an argument to functions that require it."
  },
  {
    "rule_id": "broad-exception",
    "severity": "error",
    "message": "Catching a broad `Exception` can hide unexpected bugs and make debugging difficult.",
    "line": 31,
    "suggestion": "Catch specific exceptions, such as `requests.exceptions.JSONDecodeError`."
  },
  {
    "rule_id": "broad-exception",
    "severity": "error",
    "message": "Catching a broad `Exception` can hide unexpected bugs and make debugging difficult.",
    "line": 54,
    "suggestion": "Catch specific exceptions related to the network logic being executed."
  },
  {
    "rule_id": "broad-exception",
    "severity": "error",
    "message": "Catching a broad `Exception` can hide unexpected bugs and make debugging difficult.",
    "line": 61,
    "suggestion": "Catch specific exceptions or remove the try-except block if `SESSION.close()` is guaranteed to be safe."
  }
]
```