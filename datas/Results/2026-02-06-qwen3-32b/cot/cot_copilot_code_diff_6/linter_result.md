[
  {
    "rule_id": "bad-constant-name",
    "severity": "warning",
    "message": "Constant name 'ANOTHER_GLOBAL' is not descriptive",
    "line": 4,
    "suggestion": "Rename to a meaningful constant like 'POSTS_BASE_URL'"
  },
  {
    "rule_id": "bad-function-name",
    "severity": "warning",
    "message": "Function name 'functionThatDoesTooMuchAndIsHardToUnderstand' is negative and uninformative",
    "line": 6,
    "suggestion": "Rename to descriptive positive name like 'fetch_post_and_create'"
  },
  {
    "rule_id": "bad-variable-name",
    "severity": "warning",
    "message": "Variable name 'weirdVariableName' is non-descriptive",
    "line": 26,
    "suggestion": "Use meaningful name like 'create_post_response'"
  },
  {
    "rule_id": "broad-exception-catch",
    "severity": "error",
    "message": "Catching all exceptions without specific handling or logging",
    "line": 13,
    "suggestion": "Catch specific exceptions or re-raise after logging"
  },
  {
    "rule_id": "broad-exception-catch",
    "severity": "error",
    "message": "Catching all exceptions without specific handling or logging",
    "line": 23,
    "suggestion": "Catch specific exceptions or re-raise after logging"
  },
  {
    "rule_id": "no-global-variables",
    "severity": "error",
    "message": "Global variable 'GLOBAL_SESSION' used. Breaks modularity and testability",
    "line": 3,
    "suggestion": "Replace with dependency injection or context manager"
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "Function lacks docstring explaining purpose and behavior",
    "line": 6,
    "suggestion": "Add descriptive docstring for function documentation"
  }
]