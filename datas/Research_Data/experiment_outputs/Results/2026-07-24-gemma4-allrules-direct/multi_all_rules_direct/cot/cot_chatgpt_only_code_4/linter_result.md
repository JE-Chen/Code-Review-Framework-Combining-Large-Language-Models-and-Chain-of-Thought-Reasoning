```json
[
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "The 'CONFIG' dictionary is a global mutable state. Modifying it at runtime can lead to unpredictable behavior and makes the code harder to test.",
    "line": 3,
    "suggestion": "Pass configuration as an object or parameters to the classes that need them."
  },
  {
    "rule_id": "single-responsibility",
    "severity": "info",
    "message": "The 'ReportFormatter.format' method depends directly on the global 'CONFIG' state, mixing formatting logic with configuration retrieval.",
    "line": 61,
    "suggestion": "Pass the 'uppercase' flag as an argument to the 'format' method."
  },
  {
    "rule_id": "performance-bottleneck",
    "severity": "warning",
    "message": "String concatenation using '+' inside a loop is inefficient in Python as it creates a new string object in each iteration.",
    "line": 64,
    "suggestion": "Collect strings in a list and use ''.join(list) at the end."
  },
  {
    "rule_id": "performance-bottleneck",
    "severity": "warning",
    "message": "String concatenation using '+' inside a loop is inefficient in Python.",
    "line": 83,
    "suggestion": "Use ''.join() or avoid the loop if the operation is a simple identity copy."
  },
  {
    "rule_id": "naming-clarity",
    "severity": "info",
    "message": "Variable name 'r' is too short and not descriptive.",
    "line": 63,
    "suggestion": "Rename 'r' to 'row'."
  },
  {
    "rule_id": "naming-clarity",
    "severity": "info",
    "message": "Variable name 'fmt' is an abbreviation.",
    "line": 94,
    "suggestion": "Rename 'fmt' to 'format_type' or 'export_format'."
  },
  {
    "rule_id": "deeply-nested-logic",
    "severity": "info",
    "message": "Nested if-statements in 'create_exporter' increase cognitive load.",
    "line": 97,
    "suggestion": "Use a mapping dictionary or guard clauses to flatten the logic."
  }
]
```