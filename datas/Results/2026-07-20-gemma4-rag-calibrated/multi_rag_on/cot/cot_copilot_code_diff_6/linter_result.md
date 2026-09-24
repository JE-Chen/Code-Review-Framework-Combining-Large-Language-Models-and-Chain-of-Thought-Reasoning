```json
[
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "Use of global mutable state (GLOBAL_SESSION) can introduce hidden coupling and make testing difficult.",
    "line": 3,
    "suggestion": "Pass the session object as an argument to the function or encapsulate it within a class."
  },
  {
    "rule_id": "naming-convention",
    "severity": "info",
    "message": "Function name 'functionThatDoesTooMuchAndIsHardToUnderstand' does not follow PEP 8 snake_case convention.",
    "line": 6,
    "suggestion": "Rename to 'function_that_does_too_much_and_is_hard_to_understand' or a more descriptive name."
  },
  {
    "rule_id": "broad-exception",
    "severity": "error",
    "message": "Catching broad exception 'Exception' can hide real bugs and make debugging difficult.",
    "line": 12,
    "suggestion": "Catch specific exceptions, such as 'requests.exceptions.RequestException'."
  },
  {
    "rule_id": "broad-exception",
    "severity": "error",
    "message": "Bare 'except:' clause is used, which catches all exceptions including SystemExit and KeyboardInterrupt.",
    "line": 22,
    "suggestion": "Specify the exception type to be caught (e.g., 'except requests.exceptions.RequestException:')."
  },
  {
    "rule_id": "naming-convention",
    "severity": "info",
    "message": "Variable name 'weirdVariableName' does not follow PEP 8 snake_case convention.",
    "line": 25,
    "suggestion": "Rename to 'weird_variable_name' or a more descriptive name."
  }
]
```