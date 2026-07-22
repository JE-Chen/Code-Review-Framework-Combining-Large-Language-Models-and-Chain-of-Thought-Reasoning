```json
[
  {
    "rule_id": "time-dependent-logic",
    "severity": "warning",
    "message": "Direct call to time.time() makes the code non-deterministic and harder to test.",
    "line": 114,
    "suggestion": "Inject a clock provider or use a wrapper for time-related operations."
  },
  {
    "rule_id": "time-dependent-logic",
    "severity": "warning",
    "message": "Direct call to time.time() makes the code non-deterministic and harder to test.",
    "line": 118,
    "suggestion": "Inject a clock provider or use a wrapper for time-related operations."
  },
  {
    "rule_id": "single-responsibility",
    "severity": "info",
    "message": "ReportFormatter.format handles both the logic of case conversion and the structural formatting of the report.",
    "line": 66,
    "suggestion": "Separate the case conversion logic from the string concatenation logic."
  },
  {
    "rule_id": "unnecessary-work-in-loop",
    "severity": "warning",
    "message": "The loop in ReportService.generate manually concatenates characters into a buffer, which is inefficient and redundant since 'prepared' is already a string.",
    "line": 86,
    "suggestion": "Remove the loop and use the 'prepared' variable directly."
  },
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "The global CONFIG dictionary is mutated throughout the application, which can lead to unpredictable behavior in multi-threaded environments or complex test suites.",
    "line": 3,
    "suggestion": "Pass a configuration object to the classes that need it instead of relying on a global mutable dictionary."
  },
  {
    "rule_id": "naming-conventions",
    "severity": "info",
    "message": "Variable name 'r' is not descriptive.",
    "line": 68,
    "suggestion": "Rename 'r' to 'row'."
  },
  {
    "rule_id": "naming-conventions",
    "severity": "info",
    "message": "Variable name 'ch' is not descriptive.",
    "line": 87,
    "suggestion": "Rename 'ch' to 'char'."
  }
]
```