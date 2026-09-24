[
  {
    "rule_id": "override-user-agent",
    "severity": "error",
    "message": "Function overrides caller's User-Agent header, preventing caller from setting intended User-Agent.",
    "line": 13,
    "suggestion": "Only set User-Agent if not provided by caller."
  },
  {
    "rule_id": "cache-key-missing-headers",
    "severity": "error",
    "message": "Cache key does not include headers, causing incorrect caching for same URL with different headers.",
    "line": 9,
    "suggestion": "Include headers in cache key (e.g., by hashing headers)."
  },
  {
    "rule_id": "confusing-function-name",
    "severity": "warning",
    "message": "Function named 'hash' conflicts with built-in function and is ambiguous.",
    "line": 26,
    "suggestion": "Rename to 'compute_md5' or similar."
  },
  {
    "rule_id": "missing-input-validation",
    "severity": "warning",
    "message": "Function does not validate input is string, risking TypeError on non-string input.",
    "line": 28,
    "suggestion": "Validate input is string or add type conversion."
  },
  {
    "rule_id": "inefficient-memory-use",
    "severity": "warning",
    "message": "Entire response is held in memory before writing, inefficient for large files.",
    "line": 43,
    "suggestion": "Write chunks directly to disk without buffering entire response."
  },
  {
    "rule_id": "missing-exception-handling",
    "severity": "warning",
    "message": "No exception handling for failed requests or disk writes, causing program crash on error.",
    "line": 32,
    "suggestion": "Add try/except blocks to handle errors gracefully."
  },
  {
    "rule_id": "shared-cache-across-modes",
    "severity": "error",
    "message": "Cache is shared across different request modes (e.g., 'bot' and 'desktop'), leading to incorrect responses.",
    "line": 71,
    "suggestion": "Ensure cache key includes the mode or use separate cache per mode."
  },
  {
    "rule_id": "inefficient-response-read",
    "severity": "warning",
    "message": "Entire response body is read into memory for hashing, inefficient for large responses.",
    "line": 55,
    "suggestion": "Consider streaming response for hashing if response is large."
  },
  {
    "rule_id": "missing-exception-handling",
    "severity": "warning",
    "message": "No exception handling for failed fetches, causing program crash on error.",
    "line": 81,
    "suggestion": "Add exception handling to skip failed URLs."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "No docstrings provided for functions, reducing code readability and maintainability.",
    "line": 5,
    "suggestion": "Add docstrings to all public functions explaining purpose and parameters."
  }
]