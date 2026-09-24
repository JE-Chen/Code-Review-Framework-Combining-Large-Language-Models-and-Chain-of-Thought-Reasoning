```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 'GLOBAL_THING' uses a generic name that does not describe the purpose or content of the data.",
    "line": 11,
    "suggestion": "Rename to something more descriptive, e.g., 'APP_STATE' or 'SESSION_DATA'."
  },
  {
    "rule_id": "software-engineering-standard",
    "severity": "warning",
    "message": "Use of a global mutable dictionary for state management makes the code harder to test and maintain.",
    "line": 11,
    "suggestion": "Encapsulate state within a class or pass a state object to the MyWindow constructor."
  },
  {
    "rule_id": "performance-security",
    "severity": "error",
    "message": "Calling 'time.sleep()' on the main GUI thread blocks the event loop, causing the application to freeze/hang.",
    "line": 48,
    "suggestion": "Remove the sleep call or use a QTimer/worker thread for delayed execution."
  },
  {
    "rule_id": "naming-convention",
    "severity": "info",
    "message": "Method name 'do_periodic_stuff' is vague and does not describe the actual behavior of the function.",
    "line": 61,
    "suggestion": "Rename to something more specific, e.g., 'update_ui_elements'."
  }
]
```