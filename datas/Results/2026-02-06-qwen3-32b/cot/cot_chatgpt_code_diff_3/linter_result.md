[
  {
    "rule_id": "no-global-state",
    "severity": "warning",
    "message": "Global state used; should be avoided for maintainability and testability.",
    "line": 11,
    "suggestion": "Replace with instance variables or a dedicated state manager."
  },
  {
    "rule_id": "blocking-ui",
    "severity": "error",
    "message": "Blocking the main event loop with time.sleep() causes UI freeze.",
    "line": 49,
    "suggestion": "Use non-blocking methods (e.g., QTimer) instead of time.sleep()."
  },
  {
    "rule_id": "missing-docs",
    "severity": "warning",
    "message": "Class is missing a docstring.",
    "line": 18,
    "suggestion": "Add a docstring describing the class purpose and usage."
  }
]