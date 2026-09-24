```json
[
  {
    "rule_id": "mutable-default-argument",
    "severity": "error",
    "message": "Function arguments 'y' and 'z' use mutable default values (list and dict). These are shared across all calls to the function.",
    "line": 13,
    "suggestion": "Use 'None' as the default value and initialize the mutable object inside the function body."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'do_everything_and_nothing_at_once' is not descriptive and does not follow semantic clarity standards.",
    "line": 13,
    "suggestion": "Rename the function to reflect its actual purpose (e.g., 'analyze_random_data')."
  },
  {
    "rule_id": "bare-except",
    "severity": "error",
    "message": "Bare 'except:' clause catches all exceptions, including SystemExit and KeyboardInterrupt, which can hide bugs.",
    "line": 27,
    "suggestion": "Specify the expected exception (e.g., 'except ValueError:') or use 'except Exception:'."
  },
  {
    "rule_id": "performance-bottleneck",
    "severity": "warning",
    "message": "Iterating through a DataFrame using 'range(len(df))' and 'iloc' is highly inefficient.",
    "line": 45,
    "suggestion": "Use vectorized pandas operations or 'df.apply()' to perform calculations."
  },
  {
    "rule_id": "bare-except",
    "severity": "error",
    "message": "Bare 'except:' clause used in exception handling for 'weird_sum' calculation.",
    "line": 51,
    "suggestion": "Specify the exception type or remove the try-except block if the logic can be handled via vectorization."
  },
  {
    "rule_id": "bare-except",
    "severity": "error",
    "message": "Bare 'except:' clause used when assigning 'df[\"flag\"]'.",
    "line": 71,
    "suggestion": "Specify the exception type."
  },
  {
    "rule_id": "naming-convention",
    "severity": "info",
    "message": "Variable names like 'GLOBAL_THING', 'STRANGE_CACHE', and 'weird_sum' lack professional semantic clarity.",
    "line": 9,
    "suggestion": "Use descriptive names that explain the data's purpose."
  }
]
```