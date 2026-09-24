```json
[
  {
    "rule_id": "shared-mutable-state",
    "severity": "error",
    "message": "Use of global mutable state (GLOBAL_TEXT, GLOBAL_COUNTER, GLOBAL_MODE) introduces hidden coupling and makes the code difficult to test and reason about.",
    "line": 4,
    "suggestion": "Encapsulate these variables as instance attributes within the MainWindow class or a separate state management object."
  },
  {
    "rule_id": "shared-mutable-state",
    "severity": "error",
    "message": "Mutation of global state using the 'global' keyword creates side effects that bypass object-oriented encapsulation.",
    "line": 33,
    "suggestion": "Move state logic into class methods and use 'self' to access and modify instance variables."
  },
  {
    "rule_id": "shared-mutable-state",
    "severity": "error",
    "message": "Mutation of global state using the 'global' keyword creates side effects that bypass object-oriented encapsulation.",
    "line": 43,
    "suggestion": "Move state logic into class methods and use 'self' to access and modify instance variables."
  },
  {
    "rule_id": "shared-mutable-state",
    "severity": "error",
    "message": "Mutation of global state using the 'global' keyword creates side effects that bypass object-oriented encapsulation.",
    "line": 55,
    "suggestion": "Move state logic into class methods and use 'self' to access and modify instance variables."
  },
  {
    "rule_id": "naming-convention",
    "severity": "info",
    "message": "Variable names like 'btn1', 'btn2', 'input1', and 'label1' are not descriptive and lack semantic meaning.",
    "line": 13,
    "suggestion": "Rename variables to reflect their purpose (e.g., 'add_text_button', 'status_label', 'input_field')."
  }
]
```