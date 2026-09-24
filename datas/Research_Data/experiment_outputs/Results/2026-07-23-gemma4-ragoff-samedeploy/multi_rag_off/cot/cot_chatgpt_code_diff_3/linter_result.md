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
    "rule_id": "software-engineering-standard",
    "severity": "warning",
    "message": "Use of global state ('GLOBAL_THING') makes the code harder to test and maintain, and creates tight coupling between the window and the state.",
    "line": 11,
    "suggestion": "Pass a state object into the MyWindow constructor or use a proper state management pattern."
  },
  {
    "rule_id": "performance-security",
    "severity": "error",
    "message": "Calling 'time.sleep()' on the main GUI thread blocks the event loop, causing the application to freeze and become unresponsive.",
    "line": 48,
    "suggestion": "Remove the sleep call or use a QTimer/worker thread for delayed execution."
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