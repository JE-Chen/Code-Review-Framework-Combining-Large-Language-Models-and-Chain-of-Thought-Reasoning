```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 'GLOBAL_DATA_THING' is not descriptive and uses a vague suffix ('THING').",
    "line": 25,
    "suggestion": "Rename to something descriptive, e.g., 'GLOBAL_ANALYSIS_DATA'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function 'make_data_somehow' has a non-descriptive and unprofessional name.",
    "line": 64,
    "suggestion": "Rename to 'generate_dataset' or 'populate_data'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function 'analyze_in_a_hurry' has a non-descriptive and unprofessional name.",
    "line": 101,
    "suggestion": "Rename to 'perform_analysis' or 'calculate_metrics'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function 'do_something_questionable' has a non-descriptive and unprofessional name.",
    "line": 153,
    "suggestion": "Rename to 'validate_results' or 'process_extra_metrics'."
  },
  {
    "rule_id": "bare-except",
    "severity": "error",
    "message": "Bare 'except:' clause catches all exceptions, including SystemExit and KeyboardInterrupt, which can hide bugs.",
    "line": 85,
    "suggestion": "Catch specific exceptions, e.g., 'except Exception:' or 'except pandas.errors.PandasError:'."
  },
  {
    "rule_id": "bare-except",
    "severity": "error",
    "message": "Bare 'except:' clause used during DataFrame operation.",
    "line": 117,
    "suggestion": "Catch specific exceptions to avoid masking logic errors."
  },
  {
    "rule_id": "bare-except",
    "severity": "error",
    "message": "Bare 'except:' clause used inside a loop, which can lead to silent failures for every iteration.",
    "line": 126,
    "suggestion": "Catch specific exceptions and log the error."
  },
  {
    "rule_id": "software-engineering-standard",
    "severity": "warning",
    "message": "Use of 'global' variables ('GLOBAL_DATA_THING', 'GLOBAL_FLAG') reduces modularity and makes testing difficult.",
    "line": 65,
    "suggestion": "Encapsulate data within the 'EverythingWindow' class or a dedicated DataManager class."
  },
  {
    "rule_id": "performance",
    "severity": "warning",
    "message": "Using 'df.iloc[i]' inside a for-loop is significantly slower than using vectorized pandas operations or 'itertuples()'.",
    "line": 123,
    "suggestion": "Refactor the loop using pandas vectorization (e.g., 'df['mix'].where(df['mix'] > 0, df['gamma'].abs()).sum()')."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "error",
    "message": "Potential crash: 'len(GLOBAL_DATA_THING)' is called on line 89 without verifying if 'GLOBAL_DATA_THING' is None (which happens if the try-except on line 85 fails).",
    "line": 89,
    "suggestion": "Add a check: 'if GLOBAL_DATA_THING is not None:' before accessing its length."
  }
]
```