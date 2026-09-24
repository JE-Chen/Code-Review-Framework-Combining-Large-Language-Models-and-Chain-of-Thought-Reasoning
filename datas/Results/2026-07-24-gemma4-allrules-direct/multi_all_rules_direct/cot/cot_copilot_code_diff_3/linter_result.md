```json
[
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "Use of global variable 'globalLabel' introduces hidden coupling and makes the code harder to reason about.",
    "line": 5,
    "suggestion": "Encapsulate the label as an instance attribute of the window class."
  },
  {
    "rule_id": "naming-conventions",
    "severity": "info",
    "message": "Function name 'veryStrangeFunctionNameThatDoesTooMuch' is overly verbose and does not follow standard naming conventions (e.g., PEP 8).",
    "line": 8,
    "suggestion": "Rename to something descriptive and concise, such as 'setup_ui_layout'."
  },
  {
    "rule_id": "single-responsibility",
    "severity": "warning",
    "message": "The function 'veryStrangeFunctionNameThatDoesTooMuch' handles layout creation, widget instantiation, and event binding simultaneously.",
    "line": 8,
    "suggestion": "Split the function into smaller, focused methods (e.g., 'init_widgets' and 'setup_connections')."
  },
  {
    "rule_id": "deeply-nested-logic",
    "severity": "info",
    "message": "Deeply nested function definitions ('inner' and 'inner2') increase cognitive load.",
    "line": 18,
    "suggestion": "Refactor nested functions into separate methods of the class."
  }
]
```