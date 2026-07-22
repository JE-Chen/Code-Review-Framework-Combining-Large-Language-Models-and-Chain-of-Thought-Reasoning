[
  {
    "rule_id": "bad-naming",
    "severity": "warning",
    "message": "Parameter 'flag' is not descriptive. Use 'force_active' or similar to clarify intent.",
    "line": 16,
    "suggestion": "Rename parameter to 'force_active' for clarity."
  },
  {
    "rule_id": "broad-exception",
    "severity": "warning",
    "message": "Catching all exceptions (Exception) is too broad. Missing specific error handling.",
    "line": 27,
    "suggestion": "Catch specific exceptions like json.JSONDecodeError and log errors."
  },
  {
    "rule_id": "redundant-variable",
    "severity": "warning",
    "message": "Variable 'temp' is redundant and unnecessary. Direct iteration over 'raw' suffices.",
    "line": 32,
    "suggestion": "Replace with direct iteration: 'for item in raw:'"
  },
  {
    "rule_id": "unnecessary-type-cast",
    "severity": "warning",
    "message": "Unnecessary conversion to string and back to float. Float value is already valid.",
    "line": 77,
    "suggestion": "Remove type conversion: return avg directly."
  },
  {
    "rule_id": "commented-out-code",
    "severity": "warning",
    "message": "Commented-out code blocks should be removed to avoid confusion.",
    "line": 100,
    "suggestion": "Delete the commented code block."
  },
  {
    "rule_id": "resource-leak",
    "severity": "warning",
    "message": "File opened without context manager risks resource leaks.",
    "line": 23,
    "suggestion": "Use 'with open(DATA_FILE, 'r') as f:' for safe resource handling."
  },
  {
    "rule_id": "global-state",
    "severity": "warning",
    "message": "Global variable '_cache' creates hidden dependencies and state coupling.",
    "line": 60,
    "suggestion": "Avoid global state; use dependency injection or cache object."
  },
  {
    "rule_id": "redundant-count",
    "severity": "warning",
    "message": "Manual count of users is redundant; len(users) is more efficient.",
    "line": 66,
    "suggestion": "Replace count variable with len(users)."
  },
  {
    "rule_id": "inconsistent-return-type",
    "severity": "warning",
    "message": "Function returns inconsistent types (User or dict) based on score.",
    "line": 94,
    "suggestion": "Return consistent type (e.g., always User or always dict)."
  },
  {
    "rule_id": "missing-error-handling",
    "severity": "warning",
    "message": "File write operation lacks error handling for I/O failures.",
    "line": 140,
    "suggestion": "Add try/except block for file operations."
  },
  {
    "rule_id": "missing-exist-ok",
    "severity": "warning",
    "message": "Directory creation should specify 'exist_ok=True' to avoid errors on existing directories.",
    "line": 131,
    "suggestion": "Use os.makedirs('./data', exist_ok=True)."
  }
]