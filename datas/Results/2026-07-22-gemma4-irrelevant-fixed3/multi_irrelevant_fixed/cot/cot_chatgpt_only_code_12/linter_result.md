```json
[
  {
    "rule_id": "mutable-default-argument",
    "severity": "error",
    "message": "Function uses mutable default arguments (y=[] and z={\"a\": 1}), which are shared across all calls to the function.",
    "line": 13,
    "suggestion": "Use None as the default value and initialize the list/dict inside the function body."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'do_everything_and_nothing_at_once' is not descriptive and lacks semantic clarity.",
    "line": 13,
    "suggestion": "Rename the function to reflect its actual purpose (e.g., 'analyze_random_data')."
  },
  {
    "rule_id": "global-variable-usage",
    "severity": "warning",
    "message": "Use of 'global GLOBAL_THING' makes the function harder to test and maintain by introducing side effects.",
    "line": 14,
    "suggestion": "Pass the state as an argument or return it as part of the result."
  },
  {
    "rule_id": "bare-except",
    "severity": "error",
    "message": "Bare 'except:' clause catches all exceptions, including SystemExit and KeyboardInterrupt, masking potential bugs.",
    "line": 27,
    "suggestion": "Specify the expected exception (e.g., 'except ValueError:')."
  },
  {
    "rule_id": "performance-bottleneck",
    "severity": "warning",
    "message": "Iterating through a DataFrame using 'range(len(df))' and 'iloc' is highly inefficient.",
    "line": 46,
    "suggestion": "Use vectorized pandas operations or 'df.apply()' to calculate 'weird_sum'."
  },
  {
    "rule_id": "bare-except",
    "severity": "error",
    "message": "Bare 'except Exception as e:' is used but the exception 'e' is never utilized, and the logic simply adds 0.",
    "line": 52,
    "suggestion": "Remove the try-except block or handle specific errors meaningfully."
  },
  {
    "rule_id": "bare-except",
    "severity": "error",
    "message": "Bare 'except:' clause used during flag assignment.",
    "line": 72,
    "suggestion": "Specify the expected exception or validate the data before the operation."
  },
  {
    "rule_id": "naming-convention",
    "severity": "info",
    "message": "Variable names like 'weird_sum', 'temp', and 'something_useless' are not descriptive.",
    "line": 45,
    "suggestion": "Use meaningful names that describe the data the variable holds."
  }
]
```