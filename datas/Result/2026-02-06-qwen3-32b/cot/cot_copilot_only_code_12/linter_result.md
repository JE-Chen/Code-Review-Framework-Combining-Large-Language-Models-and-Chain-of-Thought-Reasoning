[
  {
    "rule_id": "naming-constant-mutable",
    "severity": "warning",
    "message": "Global variable `DATAFRAME` is named in uppercase but is mutable. Use snake_case for variables.",
    "line": 6,
    "suggestion": "Rename to `dataframe`."
  },
  {
    "rule_id": "naming-variable",
    "severity": "warning",
    "message": "Variable name `resultList` uses camelCase. Use snake_case for variable names.",
    "line": 7,
    "suggestion": "Rename to `result_list`."
  },
  {
    "rule_id": "naming-variable",
    "severity": "warning",
    "message": "Variable name `tempStorage` uses camelCase. Use snake_case for variable names.",
    "line": 8,
    "suggestion": "Rename to `temp_storage`."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "Function `loadData` is missing a docstring.",
    "line": 10,
    "suggestion": "Add a docstring describing the function."
  },
  {
    "rule_id": "no-global",
    "severity": "warning",
    "message": "Function `loadData` uses global variable `DATAFRAME`. Avoid global state for better testability.",
    "line": 11,
    "suggestion": "Return the DataFrame and assign it in the caller."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "Function `calcStats` is missing a docstring.",
    "line": 19,
    "suggestion": "Add a docstring describing the function."
  },
  {
    "rule_id": "no-global",
    "severity": "warning",
    "message": "Function `calcStats` uses global variables `DATAFRAME` and `resultList`. Avoid global state for better testability.",
    "line": 20,
    "suggestion": "Pass DataFrame and resultList as parameters."
  },
  {
    "rule_id": "unnecessary-computation",
    "severity": "warning",
    "message": "Column 'A' is processed twice: mean calculated and then recalculated for 'meanA_again'.",
    "line": 27,
    "suggestion": "Remove the redundant calculation."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "Function `plotData` is missing a docstring.",
    "line": 36,
    "suggestion": "Add a docstring describing the function."
  },
  {
    "rule_id": "no-global",
    "severity": "warning",
    "message": "Function `plotData` uses global variable `DATAFRAME`. Avoid global state for better testability.",
    "line": 37,
    "suggestion": "Pass DataFrame as a parameter."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "Function `main` is missing a docstring.",
    "line": 43,
    "suggestion": "Add a docstring describing the function."
  }
]