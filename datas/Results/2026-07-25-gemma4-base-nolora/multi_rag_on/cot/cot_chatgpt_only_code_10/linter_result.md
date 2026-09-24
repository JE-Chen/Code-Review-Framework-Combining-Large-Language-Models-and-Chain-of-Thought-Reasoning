```json
[
  {
    "rule_id": "mutable-default-argument",
    "severity": "error",
    "message": "Using a mutable default argument (headers={}) can lead to unexpected behavior as the dictionary is shared across all function calls.",
    "line": 6,
    "suggestion": "Use 'headers=None' and initialize it inside the function with 'if headers is None: headers = {}'."
  },
  {
    "rule_id": "naming-collision",
    "severity": "warning",
    "message": "The function name 'hash' shadows the Python built-in 'hash()' function.",
    "line": 28,
    "suggestion": "Rename the function to 'calculate_hash' or 'get_md5_hash'."
  },
  {
    "rule_id": "single-responsibility-principle",
    "severity": "warning",
    "message": "The 'download_file' function handles network I/O, business logic (preview truncation), and file system I/O in one block.",
    "line": 34,
    "suggestion": "Split the function into a downloader and a file writer."
  },
  {
    "rule_id": "resource-management",
    "severity": "warning",
    "message": "The 'requests.get' call with 'stream=True' should be used within a context manager (with statement) to ensure the connection is closed promptly.",
    "line": 35,
    "suggestion": "Wrap the request in 'with requests.get(...) as resp:'."
  },
  {
    "rule_id": "performance-bottleneck",
    "severity": "info",
    "message": "Repeatedly concatenating bytes ('content += chunk') in a loop is inefficient for large files as it creates a new copy of the object each time.",
    "line": 43,
    "suggestion": "Collect chunks in a list and use 'b''.join(chunks)' at the end."
  }
]
```