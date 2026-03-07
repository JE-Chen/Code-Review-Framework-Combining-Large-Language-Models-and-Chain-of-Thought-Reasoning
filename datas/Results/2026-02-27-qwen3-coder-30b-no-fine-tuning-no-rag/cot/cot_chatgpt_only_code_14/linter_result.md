```json
[
  {
    "rule_id": "no-global-assign",
    "severity": "error",
    "message": "Assignment to global variable 'GLOBAL_DATA_THING' detected. Global variables should be avoided to maintain modularity.",
    "line": 38,
    "suggestion": "Refactor to use instance variables or pass data through parameters instead of relying on global state."
  },
  {
    "rule_id": "no-global-assign",
    "severity": "error",
    "message": "Assignment to global variable 'GLOBAL_FLAG' detected. Global variables should be avoided to maintain modularity.",
    "line": 39,
    "suggestion": "Refactor to use instance variables or pass data through parameters instead of relying on global state."
  },
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Unused import 'math'. Consider removing it if not used.",
    "line": 7,
    "suggestion": "Remove unused import 'math' to improve readability and reduce dependencies."
  },
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Unused import 'time'. Consider removing it if not used.",
    "suggestion": "Remove unused import 'time' to improve readability and reduce dependencies.",
    "line": 8
  },
  {
    "rule_id": "no-magic-number",
    "severity": "warning",
    "message": "Magic number '42' used. Replace with a named constant for clarity.",
    "line": 12,
    "suggestion": "Define 'MAGIC_NUMBER' as a descriptive constant like 'MAX_ALPHA_VALUE' or similar."
  },
  {
    "rule_id": "no-implicit-globals",
    "severity": "error",
    "message": "Use of global keyword in method 'make_data_somehow'. This can lead to unpredictable behavior and hard-to-debug code.",
    "line": 50,
    "suggestion": "Avoid using global variables. Pass data via constructor or methods instead."
  },
  {
    "rule_id": "no-implicit-globals",
    "severity": "error",
    "message": "Use of global keyword in method 'analyze_in_a_hurry'. This can lead to unpredictable behavior and hard-to-debug code.",
    "line": 69,
    "suggestion": "Avoid using global variables. Pass data via constructor or methods instead."
  },
  {
    "rule_id": "no-catch-exception",
    "severity": "error",
    "message": "Empty except block detected. Exception handling should at least log or re-raise exceptions.",
    "line": 48,
    "suggestion": "Replace empty except clause with specific exception handling or logging."
  },
  {
    "rule_id": "no-catch-exception",
    "severity": "error",
    "message": "Empty except block detected. Exception handling should at least log or re-raise exceptions.",
    "line": 77,
    "suggestion": "Replace empty except clause with specific exception handling or logging."
  },
  {
    "rule_id": "no-catch-exception",
    "severity": "error",
    "message": "Empty except block detected. Exception handling should at least log or re-raise exceptions.",
    "line": 86,
    "suggestion": "Replace empty except clause with specific exception handling or logging."
  },
  {
    "rule_id": "no-duplicate-code",
    "severity": "warning",
    "message": "Code block for setting table items is repeated multiple times. Consider extracting into a helper method.",
    "line": 58,
    "suggestion": "Create a helper method to populate the table to avoid duplication."
  },
  {
    "rule_id": "no-hardcoded-strings",
    "severity": "warning",
    "message": "Hardcoded string 'Status: idle-ish' found. Use constants or localization for better maintainability.",
    "line": 28,
    "suggestion": "Define status messages as constants or use a configuration dictionary."
  },
  {
    "rule_id": "no-hardcoded-strings",
    "severity": "warning",
    "message": "Hardcoded string 'Status: generating...' found. Use constants or localization for better maintainability.",
    "line": 41,
    "suggestion": "Define status messages as constants or use a configuration dictionary."
  },
  {
    "rule_id": "no-hardcoded-strings",
    "severity": "warning",
    "message": "Hardcoded string 'Status: analyzing...' found. Use constants or localization for better maintainability.",
    "line": 72,
    "suggestion": "Define status messages as constants or use a configuration dictionary."
  },
  {
    "rule_id": "no-hardcoded-strings",
    "severity": "warning",
    "message": "Hardcoded string 'Status: doing extra thing' found. Use constants or localization for better maintainability.",
    "line": 94,
    "suggestion": "Define status messages as constants or use a configuration dictionary."
  }
]
```