```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 'globalLabel' uses camelCase; Python convention (PEP 8) suggests snake_case for variables.",
    "line": 5,
    "suggestion": "Rename to 'global_label'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 'anotherGlobal' uses camelCase; Python convention (PEP 8) suggests snake_case for variables.",
    "line": 6,
    "suggestion": "Rename to 'another_global'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "error",
    "message": "Function name 'veryStrangeFunctionNameThatDoesTooMuch' is overly verbose and uses camelCase instead of snake_case.",
    "line": 8,
    "suggestion": "Rename to a concise, descriptive snake_case name (e.g., 'setup_ui')."
  },
  {
    "rule_id": "software-engineering-standards",
    "severity": "error",
    "message": "Use of 'global' keyword to modify 'globalLabel' creates hidden dependencies and makes the code harder to test and maintain.",
    "line": 9,
    "suggestion": "Pass the label as a return value or store it as an instance attribute of the window class."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "warning",
    "message": "Multiple lambda functions are connected to the same signal (btn1.clicked). The second lambda will overwrite the visual effect of the first immediately.",
    "line": 15,
    "suggestion": "Combine the logic into a single function or lambda."
  },
  {
    "rule_id": "software-engineering-standards",
    "severity": "info",
    "message": "Deeply nested functions ('inner' and 'inner2') increase cognitive complexity unnecessarily.",
    "line": 19,
    "suggestion": "Flatten the function structure by defining the logic as a separate method."
  }
]
```