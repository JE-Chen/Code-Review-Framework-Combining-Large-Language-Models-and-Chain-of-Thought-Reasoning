```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 'GLOBAL_THING' uses a generic name that does not describe the data it holds.",
    "line": 11,
    "suggestion": "Rename to something more descriptive, e.g., 'APP_STATE'."
  },
  {
    "rule_id": "software-engineering-standard",
    "severity": "warning",
    "message": "Use of a global mutable dictionary for state management makes the code harder to test and maintain.",
    "line": 11,
    "suggestion": "Encapsulate state within the MyWindow class or a dedicated State manager class."
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
    "message": "Method name 'do_periodic_stuff' is vague and not descriptive of its actual behavior.",
    "line": 61,
    "suggestion": "Rename to 'update_ui_elements' or 'refresh_random_state'."
  }
]
```