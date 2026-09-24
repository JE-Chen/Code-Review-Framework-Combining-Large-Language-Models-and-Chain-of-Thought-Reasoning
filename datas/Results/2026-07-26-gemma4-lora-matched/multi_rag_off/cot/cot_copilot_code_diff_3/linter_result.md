```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 'globalLabel' and 'anotherGlobal' do not follow PEP 8 naming conventions (should be snake_case).",
    "line": 4,
    "suggestion": "Rename to 'global_label' and 'another_global'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'veryStrangeFunctionNameThatDoesTooMuch' is overly verbose and does not follow PEP 8 naming conventions.",
    "line": 7,
    "suggestion": "Rename to a concise, snake_case name like 'setup_gui_layout'."
  },
  {
    "rule_id": "software-engineering-standard",
    "severity": "error",
    "message": "Use of 'global' keyword for 'globalLabel' creates hidden dependencies and makes the code harder to test and maintain.",
    "line": 8,
    "suggestion": "Pass the label as a return value or encapsulate it within a class as an instance attribute."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "warning",
    "message": "Multiple signal connections to 'btn1.clicked' will result in the second lambda overriding the first (the label will only ever show the second text).",
    "line": 14,
    "suggestion": "Combine the logic into a single function or lambda."
  },
  {
    "rule_id": "software-engineering-standard",
    "severity": "info",
    "message": "Deeply nested functions ('inner' and 'inner2') increase cognitive complexity unnecessarily.",
    "line": 18,
    "suggestion": "Flatten the function structure by defining the logic as a separate method."
  },
  {
    "rule_id": "naming-convention",
    "severity": "info",
    "message": "Variable 'w' is not descriptive.",
    "line": 34,
    "suggestion": "Rename to 'window' or 'main_window'."
  }
]
```