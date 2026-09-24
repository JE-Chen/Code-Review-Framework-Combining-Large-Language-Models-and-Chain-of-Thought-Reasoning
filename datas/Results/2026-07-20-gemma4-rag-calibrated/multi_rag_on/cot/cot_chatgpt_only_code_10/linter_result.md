```json
[
  {
    "rule_id": "mutable-default-argument",
    "severity": "error",
    "message": "Function 'fetch_resource' uses a mutable default argument (headers={}). This can lead to unexpected behavior as the dictionary is shared across all calls to the function.",
    "line": 6,
    "suggestion": "Use 'headers=None' and initialize it inside the function: 'if headers is None: headers = {}'."
  },
  {
    "rule_id": "naming-collision",
    "severity": "warning",
    "message": "Function name 'hash' shadows the built-in Python 'hash()' function.",
    "line": 28,
    "suggestion": "Rename the function to something more descriptive, such as 'calculate_md5_hash'."
  },
  {
    "rule_id": "resource-management",
    "severity": "warning",
    "message": "The 'requests.get' call in 'download_file' uses 'stream=True' but the response object is not closed, which can lead to leaked connections.",
    "line": 36,
    "suggestion": "Use a 'with requests.get(...) as resp:' block to ensure the connection is closed."
  },
  {
    "rule_id": "single-responsibility",
    "severity": "info",
    "message": "Function 'download_file' handles both network I/O (downloading) and file system I/O (writing to disk).",
    "line": 35,
    "suggestion": "Split the function into two: one for downloading the content and another for saving it to a file."
  }
]
```