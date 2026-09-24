```json
[
  {
    "rule_id": "security-eval",
    "severity": "error",
    "message": "Use of 'eval()' with user-supplied input is a critical security vulnerability (Remote Code Execution).",
    "line": 48,
    "suggestion": "Avoid eval(). Use safer alternatives like ast.literal_eval() or a dedicated parser."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'f' is not descriptive and lacks semantic clarity.",
    "line": 31,
    "suggestion": "Rename 'f' to reflect its mathematical purpose (e.g., 'calculate_linear_transform')."
  },
  {
    "rule_id": "exception-handling-too-broad",
    "severity": "warning",
    "message": "Catching a generic 'Exception' can hide unexpected bugs and makes debugging difficult.",
    "line": 53,
    "suggestion": "Catch specific exceptions, such as KeyError or TypeError."
  }
]
```