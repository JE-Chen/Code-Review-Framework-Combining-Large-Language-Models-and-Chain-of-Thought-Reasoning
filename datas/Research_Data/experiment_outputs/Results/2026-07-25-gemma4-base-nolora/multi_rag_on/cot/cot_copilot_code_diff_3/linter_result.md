```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 'globalLabel' uses camelCase; Python convention (PEP 8) prescribes snake_case for variables.",
    "line": 5,
    "suggestion": "Rename to 'global_label'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 'anotherGlobal' uses camelCase; Python convention (PEP 8) prescribes snake_case for variables.",
    "line": 6,
    "suggestion": "Rename to 'another_global'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'veryStrangeFunctionNameThatDoesTooMuch' is overly verbose and uses camelCase instead of snake_case.",
    "line": 8,
    "suggestion": "Rename to a concise snake_case name, e.g., 'setup_ui'."
  },
  {
    "rule_id": "software-engineering-standard",
    "severity": "error",
    "message": "Use of 'global' keyword to modify 'globalLabel' creates hidden dependencies and makes the code harder to test and maintain.",
    "line": 9,
    "suggestion": "Pass the label as a return value or encapsulate the logic within a class."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "warning",
    "message": "Multiple signal connections to 'btn1.clicked' result in the second lambda overriding the first (the label will only ever show the second text).",
    "line": 15,
    "suggestion": "Combine the logic into a single function or lambda."
  },
  {
    "rule_id": "software-engineering-standard",
    "severity": "info",
    "message": "Deeply nested functions ('inner' and 'inner2') increase cognitive complexity unnecessarily.",
    "line": 19,
    "suggestion": "Flatten the function structure by defining 'inner2' at a higher scope or as a method."
  }
]
```