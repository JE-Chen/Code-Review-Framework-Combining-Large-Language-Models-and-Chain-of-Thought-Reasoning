[
  {
    "rule_id": "bad-function-name",
    "severity": "warning",
    "message": "Function name uses camelCase and lacks descriptive meaning. Should follow snake_case conventions and clearly reflect purpose.",
    "line": 6,
    "suggestion": "Rename to descriptive snake_case name (e.g., 'analyze_sample_data')."
  },
  {
    "rule_id": "global-variable",
    "severity": "warning",
    "message": "Global variable 'GLOBAL_DF' creates hidden dependencies and breaks testability.",
    "line": 3,
    "suggestion": "Remove global; pass data as function parameters and return results."
  },
  {
    "rule_id": "bad-constant-name",
    "severity": "warning",
    "message": "Constant name 'ANOTHER_GLOBAL' is non-descriptive and fails to communicate intent.",
    "line": 4,
    "suggestion": "Rename to meaningful constant (e.g., 'ANALYSIS_START_MESSAGE')."
  },
  {
    "rule_id": "too-much-in-one-function",
    "severity": "warning",
    "message": "Function handles data creation, processing, and output simultaneously (violates SRP).",
    "line": 6,
    "suggestion": "Split into dedicated functions: 'create_sample_data()', 'process_scores()', 'print_results()'."
  },
  {
    "rule_id": "broad-exception-catch",
    "severity": "error",
    "message": "Catches all exceptions (Exception) instead of specific error types.",
    "line": 15,
    "suggestion": "Replace with specific exception handling or re-raise after logging."
  },
  {
    "rule_id": "redundant-condition",
    "severity": "warning",
    "message": "Nested condition for mean_age is redundant and complex.",
    "line": 17,
    "suggestion": "Simplify to single range check: 'if 20 < mean_age < 50:'"
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "Function lacks docstring explaining purpose, parameters, and return value.",
    "line": 6,
    "suggestion": "Add descriptive docstring for documentation and IDE support."
  }
]