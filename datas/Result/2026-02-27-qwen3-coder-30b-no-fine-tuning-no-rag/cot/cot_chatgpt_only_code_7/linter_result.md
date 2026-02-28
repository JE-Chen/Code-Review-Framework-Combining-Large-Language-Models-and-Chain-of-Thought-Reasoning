[
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Variable 'window' is defined but never used.",
    "line": 84,
    "suggestion": "Remove unused variable 'window'."
  },
  {
    "rule_id": "no-undef",
    "severity": "error",
    "message": "Undefined variable 'window' in function scope.",
    "line": 84,
    "suggestion": "Ensure all variables are properly declared before use."
  },
  {
    "rule_id": "no-global-assign",
    "severity": "error",
    "message": "Assignment to global variable 'app' is not allowed.",
    "line": 10,
    "suggestion": "Avoid assigning to global variables; consider encapsulating in a function."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '1000' found in timer start; consider using a named constant.",
    "line": 60,
    "suggestion": "Define '1000' as a named constant like 'REFRESH_INTERVAL_MS'."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic numbers '0.3' and '0.2' found in sleep calls; consider using named constants.",
    "line": 41,
    "suggestion": "Replace magic numbers with named constants such as 'ADD_DELAY_SEC' and 'DELETE_DELAY_SEC'."
  },
  {
    "rule_id": "no-empty-blocks",
    "severity": "warning",
    "message": "Empty except block found; it's better to handle exceptions explicitly.",
    "line": 33,
    "suggestion": "Add logging or raise specific exceptions inside the except block."
  },
  {
    "rule_id": "no-duplicate-key",
    "severity": "error",
    "message": "Duplicate key 'name' in dictionary literal.",
    "line": 49,
    "suggestion": "Ensure keys in dictionaries are unique and meaningful."
  },
  {
    "rule_id": "no-implicit-globals",
    "severity": "warning",
    "message": "Implicit global variable 'users' used in class method.",
    "line": 23,
    "suggestion": "Explicitly declare class attributes or pass them as parameters."
  },
  {
    "rule_id": "no-unsafe-named-params",
    "severity": "warning",
    "message": "Using lambda with no arguments may lead to confusion; prefer named functions.",
    "line": 64,
    "suggestion": "Replace lambda with named methods for better readability."
  }
]