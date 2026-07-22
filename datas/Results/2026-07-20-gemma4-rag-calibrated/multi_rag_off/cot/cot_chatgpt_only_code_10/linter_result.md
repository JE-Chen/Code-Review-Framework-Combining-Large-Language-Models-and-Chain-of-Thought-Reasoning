```json
[
  {
    "rule_id": "mutable-default-argument",
    "severity": "error",
    "message": "Function 'fetch_resource' uses a mutable default argument (headers={}). This can lead to unexpected behavior as the dictionary is shared across all calls to the function.",
    "line": 6,
    "suggestion": "Use 'headers=None' and initialize inside the function: 'if headers is None: headers = {}'"
  },
  {
    "rule_id": "shadowing-builtin",
    "severity": "warning",
    "message": "Function name 'hash' shadows the Python built-in 'hash()' function.",
    "line": 28,
    "suggestion": "Rename the function to 'calculate_hash' or 'get_md5_hash'."
  },
  {
    "rule_id": "resource-leak",
    "severity": "warning",
    "message": "The 'requests.get' call with 'stream=True' in 'download_file' should be used within a context manager to ensure the connection is closed properly.",
    "line": 36,
    "suggestion": "Use 'with requests.get(url, stream=True) as resp:'"
  },
  {
    "rule_id": "performance-bottleneck",
    "severity": "info",
    "message": "Repeated string/bytes concatenation ('content += chunk') in a loop is inefficient for large files.",
    "line": 45,
    "suggestion": "Collect chunks in a list and use 'b''.join(chunks)' or write chunks directly to the file."
  },
  {
    "rule_id": "logic-error",
    "severity": "error",
    "message": "In 'fetch_resource', the 'headers' dictionary is modified in-place ('headers[\"User-Agent\"] = ...'). Because of the mutable default argument and the way 'batch_fetch' passes the same dictionary to multiple calls, this can cause side effects.",
    "line": 15,
    "suggestion": "Create a copy of the headers dictionary before modifying it."
  }
]
```