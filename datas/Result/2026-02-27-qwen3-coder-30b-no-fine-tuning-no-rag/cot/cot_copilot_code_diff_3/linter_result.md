```json
[
  {
    "rule_id": "no-global-assign",
    "severity": "error",
    "message": "Assignment to global variable 'globalLabel' should be avoided.",
    "line": 6,
    "suggestion": "Use a local variable or pass the label as a parameter instead of modifying a global."
  },
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Unused variable 'anotherGlobal' declared but never used.",
    "line": 7,
    "suggestion": "Remove the unused global variable 'anotherGlobal'."
  },
  {
    "rule_id": "func-name-mismatch",
    "severity": "warning",
    "message": "Function name 'veryStrangeFunctionNameThatDoesTooMuch' does not clearly reflect its behavior.",
    "line": 9,
    "suggestion": "Rename the function to better describe what it does, e.g., 'setupMainWindowLayout'."
  },
  {
    "rule_id": "no-duplicate-event-handlers",
    "severity": "warning",
    "message": "Duplicate event handler connected to 'btn1.clicked'; second assignment overwrites first one.",
    "line": 15,
    "suggestion": "Only connect one lambda to 'btn1.clicked', or combine the actions into a single handler."
  },
  {
    "rule_id": "no-nested-functions",
    "severity": "warning",
    "message": "Nested function 'inner2' inside 'inner' makes code harder to read and test.",
    "line": 19,
    "suggestion": "Extract nested functions into top-level methods or use inline logic for clarity."
  },
  {
    "rule_id": "no-inline-styles",
    "severity": "info",
    "message": "Hardcoded text strings like '按我一下' and '這是一個奇怪的 GUI' should be externalized for localization.",
    "line": 12,
    "suggestion": "Move UI strings to a resource file or dictionary for easier translation and maintenance."
  }
]
```