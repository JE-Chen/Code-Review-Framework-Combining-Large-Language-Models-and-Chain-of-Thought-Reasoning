[
  {
    "rule_id": "global-mutable",
    "severity": "warning",
    "message": "Global variable 'SESSION' is mutable and named in uppercase, which is confusing and violates best practices.",
    "line": 3,
    "suggestion": "Prefer to pass the session as an argument to the client or use dependency injection."
  },
  {
    "rule_id": "global-mutable",
    "severity": "warning",
    "message": "Global variable 'GLOBAL_CACHE' is mutable and named in uppercase, which is confusing and violates best practices.",
    "line": 7,
    "suggestion": "Avoid global state. Use instance variables or dependency injection for caching."
  },
  {
    "rule_id": "client-session-management",
    "severity": "warning",
    "message": "APIClient relies on a global session instead of managing its own session.",
    "line": 16,
    "suggestion": "Initialize the session in the client's __init__ and use that session internally."
  },
  {
    "rule_id": "broad-exception-catch",
    "severity": "error",
    "message": "Catching all exceptions (Exception) is too broad and may hide critical errors.",
    "line": 21,
    "suggestion": "Catch specific exceptions (e.g., requests.exceptions.RequestException) and re-raise others."
  },
  {
    "rule_id": "unvalidated-response-type",
    "severity": "error",
    "message": "Response type not validated; expected list but may be dict (on error).",
    "line": 46,
    "suggestion": "Validate response type before processing."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "Function 'process_all' lacks a docstring.",
    "line": 39,
    "suggestion": "Add a docstring explaining the function's purpose and behavior."
  }
]