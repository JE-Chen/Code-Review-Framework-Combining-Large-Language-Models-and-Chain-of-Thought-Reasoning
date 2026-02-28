```json
[
  {
    "rule_id": "mutable-default-arg",
    "severity": "warning",
    "message": "Default argument 'headers' is a mutable object (dict). This can lead to unexpected behavior due to shared state across function calls.",
    "line": 5,
    "suggestion": "Use 'None' as default and create a new dict inside the function body."
  },
  {
    "rule_id": "global-statement",
    "severity": "error",
    "message": "Usage of global variable 'fetch_resource.cache' inside function. This makes the function non-deterministic and harder to test.",
    "line": 7,
    "suggestion": "Move caching logic outside the function or pass cache as a parameter."
  },
  {
    "rule_id": "magic-number",
    "severity": "warning",
    "message": "Magic number '1234' used as chunk size in 'download_file'. Consider defining it as a named constant.",
    "line": 31,
    "suggestion": "Define 'CHUNK_SIZE = 1234' at module level for clarity."
  },
  {
    "rule_id": "hardcoded-user-agent",
    "severity": "warning",
    "message": "Hardcoded User-Agent strings ('iPhone', 'GoogleBot', 'Desktop') make the code less flexible and harder to maintain.",
    "line": 54,
    "suggestion": "Use constants or configuration for User-Agent strings."
  },
  {
    "rule_id": "no-else-return",
    "severity": "info",
    "message": "Unnecessary 'else' clause in conditional block. Can be simplified by returning early.",
    "line": 62,
    "suggestion": "Simplify conditionals by using early returns."
  },
  {
    "rule_id": "print-statement",
    "severity": "warning",
    "message": "Use of 'print()' directly in business logic reduces testability and makes output hard to control.",
    "line": 46,
    "suggestion": "Pass logging or output handlers to functions instead of printing directly."
  },
  {
    "rule_id": "no-conditional-logic-in-main",
    "severity": "warning",
    "message": "Business logic such as checking readiness and fetching data is mixed with main execution flow.",
    "line": 79,
    "suggestion": "Extract business logic into separate functions for better modularity and testability."
  }
]
```