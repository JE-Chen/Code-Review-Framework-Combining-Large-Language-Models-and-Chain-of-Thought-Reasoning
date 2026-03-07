```json
[
  {
    "rule_id": "no-global-assign",
    "severity": "error",
    "message": "Assignment to global variable 'globalLabel' is discouraged; consider using instance variables instead.",
    "line": 6,
    "suggestion": "Replace global assignment with an instance variable in the class."
  },
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Unused variable 'anotherGlobal' declared at the top level.",
    "line": 7,
    "suggestion": "Remove unused global variable or use it in logic."
  },
  {
    "rule_id": "function-max-lines",
    "severity": "error",
    "message": "Function 'veryStrangeFunctionNameThatDoesTooMuch' exceeds recommended line count; consider breaking into smaller functions.",
    "line": 9,
    "suggestion": "Refactor logic into multiple helper functions for better readability."
  },
  {
    "rule_id": "no-inline-styles",
    "severity": "warning",
    "message": "Inline lambda functions used for event connections can reduce readability and maintainability.",
    "line": 15,
    "suggestion": "Define named methods or use partial functions for clearer separation of concerns."
  },
  {
    "rule_id": "no-nested-functions",
    "severity": "warning",
    "message": "Nested function 'inner2' inside 'inner' may decrease code clarity and testability.",
    "line": 19,
    "suggestion": "Extract nested functions into top-level or class methods."
  },
  {
    "rule_id": "no-duplicate-event-handlers",
    "severity": "error",
    "message": "Multiple event handlers connected to same signal ('btn1.clicked') which may lead to unexpected behavior.",
    "line": 15,
    "suggestion": "Ensure only one handler per signal or explicitly manage multiple handlers."
  },
  {
    "rule_id": "class-name-convention",
    "severity": "warning",
    "message": "Class name 'MyWeirdWindow' does not follow standard naming convention; prefer PascalCase with descriptive terms.",
    "line": 21,
    "suggestion": "Rename class to something more descriptive like 'MainWindow' or 'ApplicationWindow'."
  },
  {
    "rule_id": "function-name-convention",
    "severity": "warning",
    "message": "Function name 'veryStrangeFunctionNameThatDoesTooMuch' lacks clarity and violates naming conventions.",
    "line": 9,
    "suggestion": "Rename function to reflect its specific responsibility, e.g., 'setup_ui_elements'."
  }
]
```