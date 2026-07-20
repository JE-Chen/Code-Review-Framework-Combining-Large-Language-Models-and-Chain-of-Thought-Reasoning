```json
[
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "The use of a global mutable dictionary 'GLOBAL_THING' introduces hidden coupling and makes the code harder to test and reason about.",
    "line": 11,
    "suggestion": "Encapsulate the state within a class or pass it explicitly to the methods that require it."
  },
  {
    "rule_id": "magic-number",
    "severity": "info",
    "message": "The timer interval '777' is a magic number.",
    "line": 36,
    "suggestion": "Define a named constant (e.g., TIMER_INTERVAL_MS = 777) to improve readability."
  },
  {
    "rule_id": "blocking-ui-thread",
    "severity": "error",
    "message": "Calling 'time.sleep(0.1)' inside a UI event handler ('handle_click') blocks the main event loop, which can lead to application freezes or lag.",
    "line": 47,
    "suggestion": "Avoid using time.sleep in the main thread; use QTimer or asynchronous patterns if a delay is needed."
  }
]
```