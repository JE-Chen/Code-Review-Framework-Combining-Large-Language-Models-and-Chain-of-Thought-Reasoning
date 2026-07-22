```json
[
  {
    "rule_id": "security-eval",
    "severity": "error",
    "message": "Use of 'eval()' with user-provided input can lead to arbitrary code execution.",
    "line": 46,
    "suggestion": "Avoid eval(); use a safe alternative like ast.literal_eval() or a predefined mapping of allowed functions."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'f' is not descriptive and lacks semantic meaning.",
    "line": 28,
    "suggestion": "Rename 'f' to reflect its mathematical purpose or the value it calculates."
  },
  {
    "rule_id": "exception-handling-too-broad",
    "severity": "warning",
    "message": "Catching a generic 'Exception' can hide unexpected bugs and make debugging difficult.",
    "line": 51,
    "suggestion": "Catch specific exceptions, such as KeyError or TypeError."
  }
]
```