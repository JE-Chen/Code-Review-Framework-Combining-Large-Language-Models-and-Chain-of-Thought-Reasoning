```json
[
  {
    "rule_id": "global-state-mutation",
    "severity": "warning",
    "message": "Use of 'global' keyword to mutate state (USER_COUNT) can lead to race conditions in multi-threaded environments.",
    "line": 15,
    "suggestion": "Use a thread-safe data store or a database to manage application state."
  },
  {
    "rule_id": "generic-exception-handling",
    "severity": "error",
    "message": "Catching a generic 'Exception' can hide unexpected bugs and makes debugging difficult.",
    "line": 21,
    "suggestion": "Catch specific exceptions (e.g., TypeError, KeyError) and handle them explicitly."
  },
  {
    "rule_id": "potential-none-type-error",
    "severity": "error",
    "message": "The code calls 'len(item)' and 'item.upper()' without verifying that 'item' is a string. If 'request.json.get(\"item\")' returns None or a non-string type, the app will crash.",
    "line": 30,
    "suggestion": "Add a type check or validation to ensure 'item' is a string before calling string methods."
  },
  {
    "rule_id": "global-state-mutation",
    "severity": "warning",
    "message": "Use of 'global' keyword to mutate state (DATA_STORE, USER_COUNT) is not thread-safe.",
    "line": 38,
    "suggestion": "Use a thread-safe data store or a database to manage application state."
  },
  {
    "rule_id": "deeply-nested-logic",
    "severity": "info",
    "message": "The function 'complex_route' has excessive nesting (up to 5 levels), which reduces readability.",
    "line": 46,
    "suggestion": "Refactor using guard clauses (early returns) to flatten the logic."
  }
]
```