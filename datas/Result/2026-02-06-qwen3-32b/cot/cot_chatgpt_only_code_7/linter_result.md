[
  {
    "rule_id": "inconsistent-naming",
    "severity": "warning",
    "message": "Variable name 'txtAge' is not descriptive. Use a more standard name like 'age_input' or 'ageLineEdit'.",
    "line": 21,
    "suggestion": "Rename to 'age_input'."
  },
  {
    "rule_id": "inconsistent-naming",
    "severity": "warning",
    "message": "Button name 'buttonDelete' does not follow prefix convention. Use 'btn_' for button variables.",
    "line": 23,
    "suggestion": "Rename to 'btn_delete'."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "Class missing docstring.",
    "line": 11,
    "suggestion": "Add a docstring describing the MainWindow class."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "Method 'add_user' missing docstring.",
    "line": 60,
    "suggestion": "Add a docstring explaining parameters and behavior."
  },
  {
    "rule_id": "broad-exception",
    "severity": "warning",
    "message": "Catching all exceptions is unsafe. Only catch ValueError for integer conversion.",
    "line": 70,
    "suggestion": "Replace 'except:' with 'except ValueError:'."
  },
  {
    "rule_id": "blocking-ui",
    "severity": "error",
    "message": "Blocking the event loop with time.sleep() freezes the GUI. Use QTimer for non-blocking delays.",
    "line": 81,
    "suggestion": "Replace time.sleep(0.3) with a non-blocking approach."
  },
  {
    "rule_id": "blocking-ui",
    "severity": "error",
    "message": "Blocking the event loop with time.sleep() freezes the GUI. Use QTimer for non-blocking delays.",
    "line": 97,
    "suggestion": "Replace time.sleep(0.2) with a non-blocking approach."
  }
]