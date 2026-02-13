[
  {
    "rule_id": "inconsistent-return-type",
    "severity": "error",
    "message": "Function 'parse_response' returns inconsistent types: dict for non-200 responses, string for success and non-JSON.",
    "line": 21,
    "suggestion": "Return a consistent type (e.g., always return a dictionary) or handle errors through exceptions."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "warning",
    "message": "Function 'get_something' lacks a docstring describing parameters and behavior.",
    "line": 10,
    "suggestion": "Add descriptive docstring explaining function purpose, parameters, and return value."
  },
  {
    "rule_id": "inadequate-error-handling",
    "severity": "warning",
    "message": "Non-JSON responses are silently ignored with a meaningless string; error context is lost.",
    "line": 25,
    "suggestion": "Log error details and re-raise a specific exception instead of returning a string."
  },
  {
    "rule_id": "non-deterministic-behavior",
    "severity": "warning",
    "message": "Random iteration count in 'do_network_logic' causes non-deterministic execution.",
    "line": 31,
    "suggestion": "Replace random iteration count with a fixed value for testability and reliability."
  }
]