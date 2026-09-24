```json
[
  {
    "rule_id": "shared-mutable-state",
    "severity": "error",
    "message": "Use of global mutable state (DATA_STORE, USER_COUNT) introduces hidden coupling and makes the code difficult to test and thread-unsafe.",
    "line": 5,
    "suggestion": "Encapsulate state within a database or a dedicated state management class."
  },
  {
    "rule_id": "shared-mutable-state",
    "severity": "error",
    "message": "Modification of global variable 'USER_COUNT' inside a function.",
    "line": 14,
    "suggestion": "Pass state explicitly or use a thread-safe counter/database."
  },
  {
    "rule_id": "single-responsibility",
    "severity": "warning",
    "message": "The 'get_items' function handles both data retrieval and business logic for filtering/transforming items based on configuration.",
    "line": 23,
    "suggestion": "Extract the item transformation logic into a separate helper function."
  },
  {
    "rule_id": "deeply-nested-logic",
    "severity": "warning",
    "message": "Deeply nested conditional logic increases cognitive load and reduces readability.",
    "line": 26,
    "suggestion": "Use guard clauses or refactor the logic into smaller functions."
  },
  {
    "rule_id": "shared-mutable-state",
    "severity": "error",
    "message": "Modification of global variables 'DATA_STORE' and 'USER_COUNT' inside a function.",
    "line": 36,
    "suggestion": "Use a repository pattern or a database to manage data resets."
  },
  {
    "rule_id": "deeply-nested-logic",
    "severity": "error",
    "message": "Excessive nesting of conditional statements (up to 4 levels deep).",
    "line": 43,
    "suggestion": "Refactor using guard clauses (e.g., 'if not param: return ...') to flatten the structure."
  },
  {
    "rule_id": "exception-handling",
    "severity": "warning",
    "message": "Catching a generic 'Exception' can hide unexpected bugs and provides poor error granularity.",
    "line": 18,
    "suggestion": "Catch specific exceptions (e.g., KeyError, TypeError) and provide meaningful error messages."
  }
]
```