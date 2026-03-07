[
  {
    "rule_id": "invalid-min-age",
    "severity": "error",
    "message": "min_age parameter not validated as integer, causing potential 500 error for non-integer input.",
    "line": 45,
    "suggestion": "Validate min_age is a numeric string before conversion using try/except or regex."
  },
  {
    "rule_id": "list-modification-during-iteration",
    "severity": "error",
    "message": "Modifying USERS list during iteration causes skipped elements and unexpected behavior.",
    "line": 59,
    "suggestion": "Use list comprehensions or copy the list before mutation to avoid iteration issues."
  },
  {
    "rule_id": "list-modification-during-iteration",
    "severity": "error",
    "message": "Modifying USERS list during iteration causes skipped elements and unexpected behavior.",
    "line": 79,
    "suggestion": "Use list comprehensions or copy the list before mutation to avoid iteration issues."
  },
  {
    "rule_id": "unvalidated-input",
    "severity": "error",
    "message": "Input parameters x and y not validated as numbers, risking TypeError for non-numeric input.",
    "line": 100,
    "suggestion": "Validate input types before arithmetic operations using isinstance or type conversion checks."
  },
  {
    "rule_id": "manual-json-build",
    "severity": "warning",
    "message": "Manual string concatenation for JSON response is error-prone and unmaintainable.",
    "line": 129,
    "suggestion": "Use dictionary with jsonify for safe, standardized JSON generation."
  },
  {
    "rule_id": "inconsistent-response",
    "severity": "warning",
    "message": "Response format inconsistent: JSON expected but plain string returned.",
    "line": 148,
    "suggestion": "Return JSON for all endpoints using jsonify to maintain consistent API contract."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "Function lacks docstring explaining purpose and parameters.",
    "line": 10,
    "suggestion": "Add descriptive docstring for function documentation and API clarity."
  }
]