[
  {
    "rule_id": "no-global-state",
    "severity": "warning",
    "message": "Global configuration dictionary used instead of dependency injection or class configuration.",
    "line": 3,
    "suggestion": "Replace global CONFIG with dependency injection or class parameters."
  },
  {
    "rule_id": "invalid-json",
    "severity": "error",
    "message": "JsonLikeExporter returns a string that is not valid JSON (uses single quotes and lacks proper escaping).",
    "line": 44,
    "suggestion": "Use a proper JSON library or format the string correctly."
  },
  {
    "rule_id": "inefficient-string-concat",
    "severity": "warning",
    "message": "String concatenation in loop using '+'; consider using list and join for efficiency.",
    "line": 60,
    "suggestion": "Replace with list and join or string formatting."
  },
  {
    "rule_id": "inefficient-string-concat",
    "severity": "warning",
    "message": "String concatenation in loop over characters; consider using string methods or building a list.",
    "line": 76,
    "suggestion": "Avoid building strings in loops; use a list and join."
  },
  {
    "rule_id": "redundant-reassignment",
    "severity": "warning",
    "message": "Reassigning 'report' to a new value (content) after formatting; the original report is lost and the name is reused.",
    "line": 72,
    "suggestion": "Use a different variable name for the formatted content."
  },
  {
    "rule_id": "non-english-comment",
    "severity": "warning",
    "message": "Comment in Chinese; use English for consistency with team conventions.",
    "line": 17,
    "suggestion": "Translate comment to English."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "No docstrings provided for classes and methods to explain purpose and usage.",
    "line": 9,
    "suggestion": "Add docstrings for all public classes and methods."
  }
]