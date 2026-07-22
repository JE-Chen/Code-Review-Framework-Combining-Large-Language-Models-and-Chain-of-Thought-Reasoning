```json
[
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "The use of a global mutable dictionary 'STATE' introduces hidden coupling and makes the application difficult to test and scale (not thread-safe).",
    "line": 7,
    "suggestion": "Encapsulate state in a database, a cache (like Redis), or a dedicated state management object."
  },
  {
    "rule_id": "generic-exception-handling",
    "severity": "warning",
    "message": "Catching a generic 'Exception' can hide unexpected bugs and makes debugging difficult.",
    "line": 20,
    "suggestion": "Catch specific exceptions, such as 'ValueError' or 'TypeError', when converting 'x' to an integer."
  },
  {
    "rule_id": "magic-number",
    "severity": "info",
    "message": "The numbers 7 and 3 are used as magic numbers to trigger a sleep delay, which lacks semantic meaning.",
    "line": 31,
    "suggestion": "Define these as named constants (e.g., VISITS_MODULO, VISITS_THRESHOLD) to explain the intent."
  },
  {
    "rule_id": "naming-convention",
    "severity": "info",
    "message": "The function name 'health_check_but_not_really' is not descriptive and does not follow professional naming standards.",
    "line": 45,
    "suggestion": "Rename to 'health_check' or a similar descriptive name."
  }
]
```