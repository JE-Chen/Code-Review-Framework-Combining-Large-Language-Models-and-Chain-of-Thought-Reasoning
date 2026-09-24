```json
[
  {
    "rule_id": "magic-numbers",
    "severity": "warning",
    "message": "Hard-coded configuration values are used directly in the code.",
    "line": 4,
    "suggestion": "Move CONFIG to a separate configuration file or use a dedicated Config class."
  },
  {
    "rule_id": "single-responsibility",
    "severity": "warning",
    "message": "ReportFormatter.format handles both the logic of iterating through rows and the conditional formatting (uppercase).",
    "line": 61,
    "suggestion": "Separate the formatting logic from the string aggregation."
  },
  {
    "rule_id": "naming-conventions",
    "severity": "info",
    "message": "Variable name 'r' is not descriptive.",
    "line": 63,
    "suggestion": "Rename 'r' to 'row'."
  },
  {
    "rule_id": "performance-bottleneck",
    "severity": "warning",
    "message": "String concatenation using '+' inside a loop is inefficient in Python (O(n^2)).",
    "line": 64,
    "suggestion": "Use a list to collect strings and join them with ''.join() at the end."
  },
  {
    "rule_id": "naming-conventions",
    "severity": "error",
    "message": "Variable 'report' is reassigned from a Report object to a string, destroying semantic clarity.",
    "line": 81,
    "suggestion": "Use a different variable name, such as 'formatted_content'."
  },
  {
    "rule_id": "performance-bottleneck",
    "severity": "warning",
    "message": "Inefficient character-by-character string concatenation loop.",
    "line": 86,
    "suggestion": "Remove the loop entirely as 'prepared' is already a string, or use ''.join() if it were a sequence."
  },
  {
    "rule_id": "time-dependency",
    "severity": "warning",
    "message": "Direct call to time.time() makes the run method non-deterministic and harder to test.",
    "line": 108,
    "suggestion": "Inject a clock provider or use a wrapper for time measurements."
  },
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "The global CONFIG dictionary is mutated throughout the application, which can lead to unpredictable behavior in multi-threaded environments.",
    "line": 131,
    "suggestion": "Pass configuration as an object to the Application or ExportManager constructor."
  }
]
```