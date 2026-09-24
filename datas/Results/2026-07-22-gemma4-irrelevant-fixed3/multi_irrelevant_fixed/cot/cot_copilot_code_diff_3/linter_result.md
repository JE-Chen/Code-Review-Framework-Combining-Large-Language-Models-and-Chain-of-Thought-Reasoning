```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 'globalLabel' and 'anotherGlobal' do not follow PEP 8 naming conventions (should be snake_case).",
    "line": 5,
    "suggestion": "Rename to 'global_label' and 'another_global'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'veryStrangeFunctionNameThatDoesTooMuch' is overly verbose and does not follow snake_case convention.",
    "line": 8,
    "suggestion": "Rename to a concise, descriptive name like 'setup_main_layout'."
  },
  {
    "rule_id": "software-engineering-standards",
    "severity": "error",
    "message": "Use of 'global' keyword for 'globalLabel' creates hidden dependencies and makes the code harder to test and maintain.",
    "line": 9,
    "suggestion": "Pass the label as a return value or store it as an attribute of the window class."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "warning",
    "message": "Multiple signal connections to 'btn1.clicked' will execute in sequence, but the second call will immediately overwrite the text set by the first.",
    "line": 15,
    "suggestion": "Combine the logic into a single function or lambda."
  },
  {
    "rule_id": "software-engineering-standards",
    "severity": "info",
    "message": "Deeply nested functions ('inner' and 'inner2') increase complexity unnecessarily.",
    "line": 19,
    "suggestion": "Flatten the logic by defining a single handler function."
  },
  {
    "rule_id": "naming-convention",
    "severity": "info",
    "message": "Variable 'w' is not descriptive.",
    "line": 35,
    "suggestion": "Rename to 'window' or 'main_window'."
  }
]
```