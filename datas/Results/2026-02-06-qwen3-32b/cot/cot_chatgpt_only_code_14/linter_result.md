[
  {
    "rule_id": "global-mutable-state",
    "severity": "error",
    "message": "Global mutable state used. Avoid shared mutable state at module level (e.g., GLOBAL_DATA_THING).",
    "line": 22,
    "suggestion": "Encapsulate state within the class or use dependency injection instead of module-level globals."
  },
  {
    "rule_id": "global-mutable-state",
    "severity": "error",
    "message": "Global mutable state used. Avoid shared mutable state at module level (e.g., GLOBAL_FLAG).",
    "line": 23,
    "suggestion": "Encapsulate state within the class or use dependency injection instead of module-level globals."
  },
  {
    "rule_id": "magic-number",
    "severity": "warning",
    "message": "MAGIC_NUMBER is a magic number. Use a descriptive constant name.",
    "line": 24,
    "suggestion": "Rename to a meaningful constant (e.g., 'MAGIC_FACTOR')."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "Class and methods lack docstrings for documentation.",
    "line": 26,
    "suggestion": "Add docstrings explaining class purpose and method functionality."
  },
  {
    "rule_id": "blocking-ui",
    "severity": "error",
    "message": "Blocking the event loop with time.sleep() freezes the UI.",
    "line": 58,
    "suggestion": "Use QTimer or background threads for long-running operations instead of blocking sleep."
  },
  {
    "rule_id": "broad-exception",
    "severity": "warning",
    "message": "Broad exception handler hides errors. Catch specific exceptions instead of all exceptions.",
    "line": 94,
    "suggestion": "Replace broad 'except:' with specific exception handling or re-raise unexpected errors."
  },
  {
    "rule_id": "blocking-ui",
    "severity": "error",
    "message": "Blocking the event loop with time.sleep() freezes the UI.",
    "line": 128,
    "suggestion": "Use QTimer or background threads for long-running operations instead of blocking sleep."
  }
]