```json
[
  {
    "rule_id": "security-eval",
    "severity": "error",
    "message": "Use of 'eval()' with user-provided input is a critical security risk (Remote Code Execution).",
    "line": 46,
    "suggestion": "Avoid eval(); use a safe alternative like ast.literal_eval() or a dedicated parser."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'f' is not descriptive and lacks semantic meaning.",
    "line": 28,
    "suggestion": "Rename 'f' to reflect its mathematical purpose (e.g., 'calculate_linear_transform')."
  },
  {
    "rule_id": "exception-handling",
    "severity": "warning",
    "message": "Bare 'except Exception' catches all errors, which can hide unexpected bugs (e.g., KeyboardInterrupt or TypeErrors).",
    "line": 51,
    "suggestion": "Catch specific exceptions, such as KeyError or TypeError."
  }
]
```