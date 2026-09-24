```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'loadAndProcessUsers' uses camelCase; Python convention (PEP 8) prescribes snake_case.",
    "line": 20,
    "suggestion": "Rename to 'load_and_process_users'."
  },
  {
    "rule_id": "resource-management",
    "severity": "error",
    "message": "File opened using 'open()' without a context manager. If an exception occurs before 'f.close()', the file handle may remain open.",
    "line": 26,
    "suggestion": "Use 'with open(DATA_FILE, \"r\") as f:'."
  },
  {
    "rule_id": "bare-except",
    "severity": "error",
    "message": "Bare 'except:' clause catches all exceptions, including SystemExit and KeyboardInterrupt, which can make debugging difficult.",
    "line": 31,
    "suggestion": "Use 'except json.JSONDecodeError:' or 'except Exception:'."
  },
  {
    "rule_id": "redundant-code",
    "severity": "info",
    "message": "The loop creating 'temp' from 'raw' is redundant as 'raw' is already a list.",
    "line": 35,
    "suggestion": "Remove the 'temp' list and iterate over 'raw' directly."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'calculateAverage' uses camelCase; Python convention (PEP 8) prescribes snake_case.",
    "line": 62,
    "suggestion": "Rename to 'calculate_average'."
  },
  {
    "rule_id": "logic-redundancy",
    "severity": "info",
    "message": "The expression 'float(str(avg))' is redundant as 'avg' is already a float resulting from division.",
    "line": 75,
    "suggestion": "Remove 'float(str(...))' and return 'avg' directly."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'getTopUser' uses camelCase; Python convention (PEP 8) prescribes snake_case.",
    "line": 80,
    "suggestion": "Rename to 'get_top_user'."
  },
  {
    "rule_id": "type-consistency",
    "severity": "warning",
    "message": "Function 'getTopUser' returns inconsistent types: sometimes a dictionary, sometimes a User object, and sometimes None.",
    "line": 94,
    "suggestion": "Ensure the function returns a consistent type (e.g., always a User object or always a dictionary)."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'formatUser' uses camelCase; Python convention (PEP 8) prescribes snake_case.",
    "line": 98,
    "suggestion": "Rename to 'format_user'."
  },
  {
    "rule_id": "string-formatting",
    "severity": "info",
    "message": "Manual string concatenation used for building the user text string.",
    "line": 106,
    "suggestion": "Use f-strings for better readability: f'{prefix}{name} | {age} | {score} | {status}{suffix}'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'mainProcess' uses camelCase; Python convention (PEP 8) prescribes snake_case.",
    "line": 110,
    "suggestion": "Rename to 'main_process'."
  }
]
```