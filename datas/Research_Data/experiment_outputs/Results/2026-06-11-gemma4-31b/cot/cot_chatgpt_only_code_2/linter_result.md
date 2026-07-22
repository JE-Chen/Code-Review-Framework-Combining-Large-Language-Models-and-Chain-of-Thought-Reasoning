```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'loadAndProcessUsers' uses camelCase; Python standard (PEP 8) prescribes snake_case.",
    "line": 20,
    "suggestion": "Rename to 'load_and_process_users'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'calculateAverage' uses camelCase; Python standard (PEP 8) prescribes snake_case.",
    "line": 64,
    "suggestion": "Rename to 'calculate_average'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'getTopUser' uses camelCase; Python standard (PEP 8) prescribes snake_case.",
    "line": 82,
    "suggestion": "Rename to 'get_top_user'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'formatUser' uses camelCase; Python standard (PEP 8) prescribes snake_case.",
    "line": 103,
    "suggestion": "Rename to 'format_user'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'mainProcess' uses camelCase; Python standard (PEP 8) prescribes snake_case.",
    "line": 115,
    "suggestion": "Rename to 'main_process'."
  },
  {
    "rule_id": "resource-management",
    "severity": "error",
    "message": "File opened using 'open()' without a context manager or guaranteed closure in case of exception.",
    "line": 26,
    "suggestion": "Use 'with open(DATA_FILE, \"r\") as f:'."
  },
  {
    "rule_id": "exception-handling",
    "severity": "error",
    "message": "Bare 'except:' clause catches all exceptions, including SystemExit and KeyboardInterrupt.",
    "line": 31,
    "suggestion": "Use 'except json.JSONDecodeError:' or 'except Exception:'."
  },
  {
    "rule_id": "software-engineering",
    "severity": "info",
    "message": "Redundant list copying. The loop creating 'temp' from 'raw' is unnecessary.",
    "line": 35,
    "suggestion": "Iterate directly over 'raw'."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "warning",
    "message": "The 'flag' parameter overrides the 'active' status from the data source regardless of its original value.",
    "line": 45,
    "suggestion": "Verify if this business logic is intended or if it should only apply when active is False."
  },
  {
    "rule_id": "software-engineering",
    "severity": "info",
    "message": "Variable '_cache' is used as a global state, which hinders testability and thread safety.",
    "line": 16,
    "suggestion": "Pass a cache object as a parameter or use a class to encapsulate state."
  },
  {
    "rule_id": "performance",
    "severity": "info",
    "message": "Manual accumulation in 'calculateAverage' can be replaced with built-in functions.",
    "line": 67,
    "suggestion": "Use 'sum(u.score for u in users) / len(users)'."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "warning",
    "message": "Inefficient and redundant type casting: float(str(avg)).",
    "line": 77,
    "suggestion": "Remove the cast or use 'round(avg, precision)' if formatting is desired."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "error",
    "message": "Inconsistent return types: 'getTopUser' returns a User object, a dictionary, or None.",
    "line": 96,
    "suggestion": "Return a consistent type (e.g., always a User object or always a dictionary)."
  },
  {
    "rule_id": "readability",
    "severity": "info",
    "message": "String concatenation using '+' is less readable and slower than f-strings.",
    "line": 111,
    "suggestion": "Use f-string: f\"{prefix}{name} | {age} | {score} | {status}{suffix}\"."
  },
  {
    "rule_id": "documentation",
    "severity": "warning",
    "message": "Public functions lack docstrings explaining parameters and return values.",
    "line": 20,
    "suggestion": "Add PEP 257 compliant docstrings to all functions."
  }
]
```