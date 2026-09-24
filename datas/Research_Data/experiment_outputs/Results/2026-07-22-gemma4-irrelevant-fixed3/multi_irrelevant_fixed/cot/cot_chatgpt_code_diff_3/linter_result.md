```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 'GLOBAL_THING' is named like a constant (UPPER_CASE) but is used as a mutable global state object.",
    "line": 11,
    "suggestion": "Rename to 'global_state' or encapsulate the state within a class/manager."
  },
  {
    "rule_id": "software-engineering-standards",
    "severity": "error",
    "message": "Use of global mutable state ('GLOBAL_THING') makes the code harder to test and maintain.",
    "line": 11,
    "suggestion": "Pass state as an argument or store it as an attribute of the MyWindow class."
  },
  {
    "rule_id": "performance-security",
    "severity": "error",
    "message": "Calling 'time.sleep()' on the main GUI thread blocks the event loop, causing the application to freeze.",
    "line": 48,
    "suggestion": "Remove the sleep call or use a QTimer/worker thread for delays."
  },
  {
    "rule_id": "naming-convention",
    "severity": "info",
    "message": "Method name 'do_periodic_stuff' is vague and not descriptive of its actual behavior.",
    "line": 61,
    "suggestion": "Rename to 'update_ui_elements' or 'refresh_random_labels'."
  }
]
```