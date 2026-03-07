[
  {
    "rule_id": "global-variables",
    "severity": "warning",
    "message": "Use of global variables reduces modularity and testability.",
    "line": 5,
    "suggestion": "Pass data as parameters or use a class to encapsulate state."
  },
  {
    "rule_id": "variable-naming",
    "severity": "warning",
    "message": "Variable name 'resultList' does not follow snake_case convention.",
    "line": 6,
    "suggestion": "Rename to 'result_list' for consistency with Python naming standards."
  },
  {
    "rule_id": "variable-naming",
    "severity": "warning",
    "message": "Variable name 'tempStorage' does not follow snake_case convention.",
    "line": 7,
    "suggestion": "Rename to 'temp_storage' for consistency with Python naming standards."
  },
  {
    "rule_id": "function-naming",
    "severity": "warning",
    "message": "Function name 'calcStats' does not follow snake_case convention.",
    "line": 13,
    "suggestion": "Rename to 'calc_stats' for consistency with Python naming standards."
  },
  {
    "rule_id": "function-naming",
    "severity": "warning",
    "message": "Function name 'plotData' does not follow snake_case convention.",
    "line": 21,
    "suggestion": "Rename to 'plot_data' for consistency with Python naming standards."
  },
  {
    "rule_id": "magic-numbers",
    "severity": "warning",
    "message": "Magic number '7' used as bin count in histogram.",
    "line": 24,
    "suggestion": "Define '7' as a named constant for better readability."
  },
  {
    "rule_id": "hardcoded-strings",
    "severity": "warning",
    "message": "Hardcoded string 'Histogram of A (for no reason)' lacks context.",
    "line": 25,
    "suggestion": "Move string to a constant or configuration file."
  },
  {
    "rule_id": "duplicate-code",
    "severity": "warning",
    "message": "Repeated calculation of mean for column A.",
    "line": 18,
    "suggestion": "Avoid redundant computations by reusing calculated values."
  },
  {
    "rule_id": "logic-error",
    "severity": "error",
    "message": "Column 'C' is processed but not used in any meaningful way.",
    "line": 20,
    "suggestion": "Ensure all columns are handled purposefully or remove unused logic."
  },
  {
    "rule_id": "inconsistent-return",
    "severity": "warning",
    "message": "Functions do not consistently return values when appropriate.",
    "line": 10,
    "suggestion": "Make return behavior consistent across functions."
  }
]