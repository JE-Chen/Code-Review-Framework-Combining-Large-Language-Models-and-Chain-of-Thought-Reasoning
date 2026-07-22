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
    "message": "Method 'make_data_somehow' has a non-descriptive and unprofessional name.",
    "line": 65,
    "suggestion": "Rename to 'generate_data' or 'populate_dataset'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Method 'analyze_in_a_hurry' has a non-descriptive and unprofessional name.",
    "line": 101,
    "suggestion": "Rename to 'perform_analysis' or 'calculate_metrics'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Method 'do_something_questionable' has a non-descriptive and unprofessional name.",
    "line": 153,
    "suggestion": "Rename to 'validate_results' or 'process_extra_metrics'."
  },
  {
    "rule_id": "bare-except",
    "severity": "error",
    "message": "Bare 'except:' clause catches all exceptions, including SystemExit and KeyboardInterrupt, which can hide bugs.",
    "line": 86,
    "suggestion": "Catch specific exceptions, e.g., 'except Exception:' or 'except pandas.errors.PandasError:'."
  },
  {
    "rule_id": "bare-except",
    "severity": "error",
    "message": "Bare 'except:' clause used during DataFrame operation; masks potential logic errors.",
    "line": 116,
    "suggestion": "Catch specific exceptions (e.g., KeyError, TypeError)."
  },
  {
    "rule_id": "bare-except",
    "severity": "error",
    "message": "Bare 'except:' clause inside a loop can lead to silent failures and difficult debugging.",
    "line": 124,
    "suggestion": "Remove the try-except block or catch specific exceptions."
  },
  {
    "rule_id": "performance-bottleneck",
    "severity": "warning",
    "message": "Using 'df.iloc[i]' inside a for-loop is significantly slower than vectorized pandas operations.",
    "line": 121,
    "suggestion": "Use vectorized operations (e.g., 'df['mix'].sum()') instead of iterating through rows."
  },
  {
    "rule_id": "software-engineering-standard",
    "severity": "warning",
    "message": "Heavy reliance on global variables ('GLOBAL_DATA_THING', 'GLOBAL_FLAG') reduces modularity and testability.",
    "line": 66,
    "suggestion": "Encapsulate data within the 'EverythingWindow' class or a separate DataManager class."
  },
  {
    "rule_id": "performance-bottleneck",
    "severity": "info",
    "message": "Calling 'time.sleep()' on the main GUI thread freezes the interface, making the application unresponsive.",
    "line": 69,
    "suggestion": "Move long-running tasks to a separate thread using QThread or use a QTimer."
  }
]
```