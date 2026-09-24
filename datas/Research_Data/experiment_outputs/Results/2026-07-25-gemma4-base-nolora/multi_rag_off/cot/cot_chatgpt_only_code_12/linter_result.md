```json
[
  {
    "rule_id": "mutable-default-argument",
    "severity": "error",
    "message": "Function 'do_everything_and_nothing_at_once' uses mutable default arguments (y=[] and z={}). This can lead to unexpected behavior as the same list/dict is shared across all function calls.",
    "line": 14,
    "suggestion": "Use 'None' as the default value and initialize the list/dict inside the function body."
  },
  {
    "rule_id": "non-descriptive-naming",
    "severity": "warning",
    "message": "Function name 'do_everything_and_nothing_at_once' is not descriptive and does not follow semantic clarity standards.",
    "line": 14,
    "suggestion": "Rename the function to reflect its actual purpose (e.g., 'analyze_random_data')."
  },
  {
    "rule_id": "bare-except",
    "severity": "error",
    "message": "Bare 'except:' clause used. This catches all exceptions, including SystemExit and KeyboardInterrupt, which makes debugging difficult.",
    "line": 30,
    "suggestion": "Specify the expected exception (e.g., 'except ValueError:') or use 'except Exception:'."
  },
  {
    "rule_id": "performance-bottleneck",
    "severity": "warning",
    "message": "Iterating through a pandas DataFrame using 'range(len(df))' and 'iloc' is highly inefficient.",
    "line": 48,
    "suggestion": "Use vectorized pandas operations or 'df.itertuples()' / 'df.apply()' for better performance."
  },
  {
    "rule_id": "broad-exception-handling",
    "severity": "warning",
    "message": "Catching a generic 'Exception' and adding 0 to a sum is a poor way to handle errors and masks potential logic bugs.",
    "line": 54,
    "suggestion": "Identify the specific error that might occur and handle it explicitly."
  },
  {
    "rule_id": "bare-except",
    "severity": "error",
    "message": "Bare 'except:' clause used in the flag assignment block.",
    "line": 73,
    "suggestion": "Specify the expected exception type."
  },
  {
    "rule_id": "non-descriptive-naming",
    "severity": "info",
    "message": "Variable names like 'GLOBAL_THING', 'STRANGE_CACHE', and 'weird_sum' lack professional semantic clarity.",
    "line": 9,
    "suggestion": "Use descriptive names that explain the data's role (e.g., 'processed_data_cache')."
  }
]
```