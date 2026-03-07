[
  {
    "rule_id": "use-global",
    "severity": "error",
    "message": "Global variable 'DATA' is used across multiple functions, making the code non-modular and difficult to test.",
    "line": 1,
    "suggestion": "Refactor to pass data as parameters instead of relying on global state."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "warning",
    "message": "Function 'calculate_average_scores' is missing a docstring describing its purpose and return value.",
    "line": 19,
    "suggestion": "Add a docstring explaining input/output and behavior."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "warning",
    "message": "Function 'filter_high_scores' is missing a docstring.",
    "line": 30,
    "suggestion": "Add a docstring to clarify function behavior."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "warning",
    "message": "Function 'process_misc' is missing a docstring.",
    "line": 38,
    "suggestion": "Add a docstring describing input/output and logic."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "warning",
    "message": "Function 'main' is missing a docstring.",
    "line": 53,
    "suggestion": "Add a docstring explaining the main execution flow."
  },
  {
    "rule_id": "misleading-name",
    "severity": "warning",
    "message": "Function name 'filter_high_scores' is misleading; it returns individual high scores, not filtered user data.",
    "line": 30,
    "suggestion": "Rename to 'extract_high_scores' or 'get_high_scores' to reflect behavior."
  },
  {
    "rule_id": "no-empty-check",
    "severity": "warning",
    "message": "Function does not handle empty scores list, which could cause ZeroDivisionError.",
    "line": 26,
    "suggestion": "Add a check for empty scores to prevent division by zero."
  }
]