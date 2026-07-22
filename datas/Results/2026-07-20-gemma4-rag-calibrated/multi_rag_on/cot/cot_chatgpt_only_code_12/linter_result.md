```json
[
  {
    "rule_id": "mutable-default-argument",
    "severity": "error",
    "message": "Function arguments 'y' and 'z' use mutable default values (list and dict). These are shared across all calls to the function.",
    "line": 14,
    "suggestion": "Use 'None' as the default value and initialize the list/dict inside the function."
  },
  {
    "rule_id": "non-deterministic-logic",
    "severity": "warning",
    "message": "Direct call to 'random.randint' and 'random.random' makes the function non-deterministic and difficult to test.",
    "line": 17,
    "suggestion": "Inject a random seed or a random number generator object as a dependency."
  },
  {
    "rule_id": "bare-except",
    "severity": "error",
    "message": "Bare 'except:' clause catches all exceptions, including SystemExit and KeyboardInterrupt, which can hide bugs.",
    "line": 30,
    "suggestion": "Specify the expected exception type (e.g., 'except ValueError:')."
  },
  {
    "rule_id": "naming-convention",
    "severity": "info",
    "message": "Function name 'do_everything_and_nothing_at_once' is not descriptive and does not follow semantic clarity standards.",
    "line": 14,
    "suggestion": "Rename the function to reflect its actual purpose (e.g., 'analyze_and_plot_data')."
  },
  {
    "rule_id": "performance-bottleneck",
    "severity": "warning",
    "message": "Using 'df.iloc' inside a for-loop to iterate over a DataFrame is extremely slow.",
    "line": 52,
    "suggestion": "Use vectorized pandas operations or 'df.itertuples()' / 'df.apply()'."
  },
  {
    "rule_id": "bare-except",
    "severity": "error",
    "message": "Bare 'except Exception as e:' is used but the exception 'e' is never utilized, and the recovery logic is trivial.",
    "line": 57,
    "suggestion": "Remove the try-except block or handle specific exceptions meaningfully."
  },
  {
    "rule_id": "bare-except",
    "severity": "error",
    "message": "Bare 'except:' clause used during flag assignment.",
    "line": 76,
    "suggestion": "Specify the expected exception type."
  },
  {
    "rule_id": "non-deterministic-logic",
    "severity": "warning",
    "message": "Direct call to 'time.sleep' introduces environment-dependent delays that slow down tests.",
    "line": 80,
    "suggestion": "Remove unnecessary sleeps or abstract the timing logic."
  }
]
```