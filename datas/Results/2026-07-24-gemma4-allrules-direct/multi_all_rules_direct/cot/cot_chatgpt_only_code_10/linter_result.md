```json
[
  {
    "rule_id": "mutable-default-argument",
    "severity": "error",
    "message": "Function 'fetch_resource' uses a mutable default argument 'headers={}'. This can lead to shared state between function calls.",
    "line": 6,
    "suggestion": "Use 'headers=None' and initialize it as 'headers = headers or {}' inside the function."
  },
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "Function 'fetch_resource' uses a function attribute 'cache' as a shared mutable state. This makes the function harder to test and reason about.",
    "line": 7,
    "suggestion": "Pass a cache object explicitly as an argument or use a dedicated caching class/decorator."
  },
  {
    "rule_id": "modify-input-argument",
    "severity": "error",
    "message": "Function 'fetch_resource' modifies the 'headers' input argument directly. This can cause unexpected side effects for the caller.",
    "line": 15,
    "suggestion": "Create a copy of the headers dictionary before modifying it."
  },
  {
    "rule_id": "magic-number",
    "severity": "info",
    "message": "Magic numbers '1234' and '3000' are used in 'download_file' without explanation.",
    "line": 38,
    "suggestion": "Define these as named constants (e.g., CHUNK_SIZE, PREVIEW_LIMIT)."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'hash' shadows the built-in Python 'hash()' function.",
    "line": 28,
    "suggestion": "Rename the function to something more descriptive, such as 'calculate_md5'."
  },
  {
    "rule_id": "single-responsibility",
    "severity": "info",
    "message": "Function 'fetch_and_verify' performs network I/O, logging, and checksum calculation. It should be split into smaller functions.",
    "line": 51,
    "suggestion": "Separate the fetching logic from the verification/hashing logic."
  },
  {
    "rule_id": "time-dependency",
    "severity": "info",
    "message": "Direct call to 'time.sleep' in 'wait_until_ready' and 'fetch_and_verify' makes tests non-deterministic and slow.",
    "line": 101,
    "suggestion": "Abstract the sleep mechanism or use a mockable timer for testing."
  }
]
```