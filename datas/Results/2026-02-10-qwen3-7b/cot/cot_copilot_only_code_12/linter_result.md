[
  {
    "rule_id": "no-global-variable",
    "severity": "error",
    "message": "Global variables `DATAFRAME` and `tempStorage` are not used in the function logic and should be local.",
    "line": 3,
    "suggestion": "Localize these variables within function scope for clarity and memory efficiency."
  },
  {
    "rule_id": "no-descriptive-naming",
    "severity": "warning",
    "message": "Function `calcStats()` is too vague and lacks semantic clarity.",
    "line": 2,
    "suggestion": "Rename to something like `calculate_statistics()` for better meaning."
  },
  {
    "rule_id": "redundant-code",
    "severity": "error",
    "message": "Redundant code in `calcStats()` appends same data twice (e.g., `meanA` and `meanA_again`).",
    "line": 5,
    "suggestion": "Remove duplicate data and consolidate logic for efficiency."
  },
  {
    "rule_id": "unused-variable",
    "severity": "error",
    "message": "Variable `tempStorage` is never used and is a memory leak.",
    "line": 7,
    "suggestion": "Remove or clear `tempStorage` if not needed."
  },
  {
    "rule_id": "no-docstring",
    "severity": "error",
    "message": "No docstring or comment for `plotData()` or `main()` function.",
    "line": 10,
    "suggestion": "Add docstrings explaining function purpose and logic."
  },
  {
    "rule_id": "no-test-case",
    "severity": "error",
    "message": "No unit tests for `loadData()`, `calcStats()`, or `plotData()`.",
    "line": 12,
    "suggestion": "Add automated tests to ensure functionality and correctness."
  }
]