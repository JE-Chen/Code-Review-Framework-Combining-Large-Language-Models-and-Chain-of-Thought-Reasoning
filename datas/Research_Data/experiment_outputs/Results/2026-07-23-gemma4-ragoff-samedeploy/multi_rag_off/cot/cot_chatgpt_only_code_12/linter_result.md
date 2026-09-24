```json
[
  {
    "rule_id": "mutable-default-argument",
    "severity": "error",
    "message": "Function arguments 'y' and 'z' use mutable default values (list and dict). These are shared across all calls to the function.",
    "line": 13,
    "suggestion": "Use 'None' as the default value and initialize the list/dict inside the function."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'do_everything_and_nothing_at_once' is not descriptive and does not follow semantic clarity standards.",
    "line": 13,
    "suggestion": "Rename the function to reflect its actual purpose (e.g., 'analyze_random_data')."
  },
  {
    "rule_id": "global-variable-usage",
    "severity": "warning",
    "message": "Use of 'global GLOBAL_THING' makes the function harder to test and maintain by introducing side effects.",
    "line": 14,
    "suggestion": "Pass the state as an argument or return the value to be updated."
  },
  {
    "rule_id": "bare-except",
    "severity": "error",
    "message": "Bare 'except:' clause catches all exceptions, including SystemExit and KeyboardInterrupt, which can hide bugs.",
    "line": 27,
    "suggestion": "Specify the expected exception (e.g., 'except ValueError:')."
  },
  {
    "rule_id": "performance-bottleneck",
    "severity": "warning",
    "message": "Iterating through a DataFrame using 'range(len(df))' and 'iloc' is extremely slow. Pandas is designed for vectorized operations.",
    "line": 45,
    "suggestion": "Use 'df["mystery"].clip(lower=0).sum()' or similar vectorized logic."
  },
  {
    "rule_id": "bare-except",
    "severity": "error",
    "message": "Bare 'except Exception as e:' is used but the exception 'e' is never utilized, and the logic simply adds 0.",
    "line": 51,
    "suggestion": "Remove the try-except block or handle specific errors meaningfully."
  },
  {
    "rule_id": "bare-except",
    "severity": "error",
    "message": "Bare 'except:' clause used during flag assignment.",
    "line": 69,
    "suggestion": "Specify the exception type or validate the data before the operation."
  },
  {
    "rule_id": "dead-code",
    "severity": "info",
    "message": "The loop containing 'time.sleep(0.01)' serves no functional purpose in the logic.",
    "line": 72,
    "suggestion": "Remove the sleep loop."
  }
]
```