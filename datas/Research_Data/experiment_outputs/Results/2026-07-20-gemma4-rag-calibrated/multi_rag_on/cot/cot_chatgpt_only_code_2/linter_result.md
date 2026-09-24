```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'loadAndProcessUsers' does not follow PEP 8 snake_case convention.",
    "line": 20,
    "suggestion": "Rename to 'load_and_process_users'."
  },
  {
    "rule_id": "resource-management",
    "severity": "error",
    "message": "File opened without using a context manager ('with' statement), which can lead to resource leaks if an exception occurs before f.close().",
    "line": 27,
    "suggestion": "Use 'with open(DATA_FILE, \"r\") as f:'."
  },
  {
    "rule_id": "exception-handling",
    "severity": "error",
    "message": "Bare 'except:' clause catches all exceptions, including SystemExit and KeyboardInterrupt, which is discouraged.",
    "line": 32,
    "suggestion": "Use 'except json.JSONDecodeError:' or 'except Exception:'."
  },
  {
    "rule_id": "software-engineering-standards",
    "severity": "info",
    "message": "Redundant loop used to copy 'raw' list into 'temp' list.",
    "line": 36,
    "suggestion": "Remove the loop and use 'temp = raw' or 'temp = list(raw)'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'calculateAverage' does not follow PEP 8 snake_case convention.",
    "line": 62,
    "suggestion": "Rename to 'calculate_average'."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "info",
    "message": "Redundant type conversion: 'float(str(avg))' is unnecessary as 'avg' is already a float.",
    "line": 76,
    "suggestion": "Remove 'float(str(...))' and return 'avg' directly."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'getTopUser' does not follow PEP 8 snake_case convention.",
    "line": 80,
    "suggestion": "Rename to 'get_top_user'."
  },
  {
    "rule_id": "software-engineering-standards",
    "severity": "warning",
    "message": "Function returns inconsistent types (User object, dictionary, or None), which complicates the calling code's logic.",
    "line": 93,
    "suggestion": "Return a consistent type, such as always returning a User object or a dictionary."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'formatUser' does not follow PEP 8 snake_case convention.",
    "line": 97,
    "suggestion": "Rename to 'format_user'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'mainProcess' does not follow PEP 8 snake_case convention.",
    "line": 108,
    "suggestion": "Rename to 'main_process'."
  }
]
```