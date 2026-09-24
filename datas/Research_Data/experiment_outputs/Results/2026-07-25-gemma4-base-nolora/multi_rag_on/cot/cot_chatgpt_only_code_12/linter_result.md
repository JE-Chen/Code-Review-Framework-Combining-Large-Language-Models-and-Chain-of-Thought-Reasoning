```json
[
  {
    "rule_id": "mutable-default-argument",
    "severity": "error",
    "message": "Function arguments 'y' and 'z' use mutable default values (list and dict). These are shared across all calls to the function.",
    "line": 14,
    "suggestion": "Use 'None' as the default value and initialize the mutable object inside the function body."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'do_everything_and_nothing_at_once' is not descriptive and lacks semantic clarity.",
    "line": 14,
    "suggestion": "Rename the function to reflect its actual purpose (e.g., 'analyze_random_data')."
  },
  {
    "rule_id": "non-deterministic-logic",
    "severity": "error",
    "message": "Direct call to 'random.randint' and 'random.random' makes the function non-deterministic and difficult to test.",
    "line": 17,
    "suggestion": "Inject a random seed or a random number generator instance as a dependency."
  },
  {
    "rule_id": "bare-except",
    "severity": "warning",
    "message": "Bare 'except' clause catches all exceptions, including SystemExit and KeyboardInterrupt, which can hide bugs.",
    "line": 30,
    "suggestion": "Specify the expected exception (e.g., 'except ValueError:')."
  },
  {
    "rule_id": "performance-bottleneck",
    "severity": "warning",
    "message": "Using 'df.iloc' inside a for-loop to iterate over a DataFrame is extremely slow.",
    "line": 51,
    "suggestion": "Use vectorized pandas operations or 'df.itertuples()' / 'df.apply()'."
  },
  {
    "rule_id": "bare-except",
    "severity": "warning",
    "message": "Bare 'except' clause used in exception handling for 'weird_sum' calculation.",
    "line": 56,
    "suggestion": "Specify the expected exception type."
  },
  {
    "rule_id": "non-deterministic-logic",
    "severity": "error",
    "message": "Direct call to 'time.sleep' introduces environment-dependent timing logic.",
    "line": 81,
    "suggestion": "Remove unnecessary sleep calls or abstract the timer into a mockable service."
  },
  {
    "rule_id": "bare-except",
    "severity": "warning",
    "message": "Bare 'except' clause used when assigning 'df[\"flag\"]'.",
    "line": 78,
    "suggestion": "Specify the expected exception type."
  },
  {
    "rule_id": "naming-convention",
    "severity": "info",
    "message": "Variable names like 'GLOBAL_THING', 'STRANGE_CACHE', and 'weird_sum' are not professionally descriptive.",
    "line": 10,
    "suggestion": "Use names that describe the data they hold (e.g., 'processed_data_cache')."
  }
]
```