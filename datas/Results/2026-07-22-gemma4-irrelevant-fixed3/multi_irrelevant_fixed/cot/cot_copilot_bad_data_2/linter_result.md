```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'f' is not descriptive and lacks semantic clarity.",
    "line": 26,
    "suggestion": "Rename 'f' to a more descriptive name that reflects its mathematical purpose (e.g., 'calculate_linear_transform')."
  },
  {
    "rule_id": "security-risk",
    "severity": "error",
    "message": "Use of 'eval()' on user-provided input can lead to arbitrary code execution.",
    "line": 41,
    "suggestion": "Avoid 'eval()'. Use 'ast.literal_eval()' for safe evaluation of literals or implement a specific parser."
  },
  {
    "rule_id": "exception-handling",
    "severity": "warning",
    "message": "Bare 'except Exception' catches all errors, which can hide unexpected bugs or system interrupts.",
    "line": 45,
    "suggestion": "Catch specific exceptions (e.g., 'KeyError' or 'TypeError') instead of the base 'Exception' class."
  }
]
```