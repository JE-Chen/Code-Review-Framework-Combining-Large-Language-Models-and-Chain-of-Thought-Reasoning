```json
[
  {
    "rule_id": "magic-numbers",
    "severity": "warning",
    "message": "The use of hard-coded constants (1234, 5678, 9999) makes the logic opaque and difficult to maintain.",
    "line": 18,
    "suggestion": "Define these values as named constants at the top of the class or in a configuration file."
  },
  {
    "rule_id": "deeply-nested-conditionals",
    "severity": "warning",
    "message": "Deeply nested conditional logic increases cognitive load and reduces readability.",
    "line": 46,
    "suggestion": "Refactor using guard clauses or extract the logic into a separate function to flatten the structure."
  }
]
```