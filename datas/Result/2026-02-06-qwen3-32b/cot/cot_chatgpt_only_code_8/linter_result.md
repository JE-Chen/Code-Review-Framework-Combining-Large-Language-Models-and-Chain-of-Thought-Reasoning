[
  {
    "rule_id": "naming-inconsistent",
    "severity": "warning",
    "message": "Inconsistent naming for input fields: 'nameInput' vs 'txtAge'.",
    "line": 21,
    "suggestion": "Use consistent naming (e.g., 'nameInput', 'ageInput')."
  },
  {
    "rule_id": "broad-exception-catch",
    "severity": "warning",
    "message": "Bare 'except' catches all exceptions, risking hidden bugs.",
    "line": 70,
    "suggestion": "Catch specific exceptions (e.g., ValueError)."
  },
  {
    "rule_id": "ui-blocked",
    "severity": "error",
    "message": "Blocking main thread with time.sleep() freezes UI.",
    "line": 81,
    "suggestion": "Replace with non-blocking operations (e.g., QTimer)."
  },
  {
    "rule_id": "ui-blocked",
    "severity": "error",
    "message": "Blocking main thread with time.sleep() freezes UI.",
    "line": 97,
    "suggestion": "Replace with non-blocking operations (e.g., QTimer)."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "warning",
    "message": "Class 'MainWindow' lacks docstring.",
    "line": 11,
    "suggestion": "Add class-level documentation."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "warning",
    "message": "Method 'add_user' lacks docstring.",
    "line": 60,
    "suggestion": "Add method documentation."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "warning",
    "message": "Method 'delete_user' lacks docstring.",
    "line": 90,
    "suggestion": "Add method documentation."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "warning",
    "message": "Method 'refresh_status' lacks docstring.",
    "line": 105,
    "suggestion": "Add method documentation."
  }
]