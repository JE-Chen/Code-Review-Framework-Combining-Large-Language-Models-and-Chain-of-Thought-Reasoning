```json
[
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "The use of a global mutable dictionary 'GLOBAL_THING' introduces hidden coupling and makes the code harder to test and reason about.",
    "line": 11,
    "suggestion": "Encapsulate the state within the MyWindow class or a dedicated state management object and pass it explicitly."
  },
  {
    "rule_id": "magic-number",
    "severity": "info",
    "message": "Hard-coded constant '777' used for timer interval.",
    "line": 36,
    "suggestion": "Define a named constant (e.g., TIMER_INTERVAL_MS = 777) at the top of the file."
  },
  {
    "rule_id": "blocking-ui-thread",
    "severity": "error",
    "message": "Calling 'time.sleep(0.1)' inside a GUI event handler (handle_click) blocks the main event loop, causing the application to freeze.",
    "line": 47,
    "suggestion": "Remove the sleep call or use QTimer/QThread for non-blocking delays."
  },
  {
    "rule_id": "magic-number",
    "severity": "info",
    "message": "Hard-coded constant '0.3' used for probability check.",
    "line": 61,
    "suggestion": "Define a named constant (e.g., TEXT_CHANGE_PROBABILITY = 0.3)."
  }
]
```