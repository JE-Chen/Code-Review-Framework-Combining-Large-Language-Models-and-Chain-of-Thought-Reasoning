```json
[
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Parameter 'data' in function 'process' is unused.",
    "line": 38,
    "suggestion": "Remove the unused parameter 'data' or use it in the function body."
  },
  {
    "rule_id": "no-undef",
    "severity": "error",
    "message": "Variable 'result' is used before being defined in the scope.",
    "line": 45,
    "suggestion": "Ensure 'result' is initialized or defined before usage."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '10' found in '_load_random_users'; consider extracting to a constant.",
    "line": 29,
    "suggestion": "Replace magic number with a named constant like MAX_USERS=10."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '100' found in '_load_random_users'; consider extracting to a constant.",
    "line": 29,
    "suggestion": "Replace magic number with a named constant like MAX_USER_ID=100."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '0.05' found in '_load_random_users'; consider extracting to a constant.",
    "line": 27,
    "suggestion": "Replace magic number with a named constant like SLEEP_DURATION=0.05."
  },
  {
    "rule_id": "no-implicit-globals",
    "severity": "error",
    "message": "Global variable 'CONFIG' is declared but not properly scoped; consider using module-level constants.",
    "line": 5,
    "suggestion": "Move 'CONFIG' into a dedicated configuration module or make it explicitly global via 'global CONFIG'."
  },
  {
    "rule_id": "no-unsafe-finally",
    "severity": "error",
    "message": "Exception handling uses bare 'except:' clause which can hide unexpected errors.",
    "line": 19,
    "suggestion": "Catch specific exceptions instead of using a bare 'except:' clause."
  },
  {
    "rule_id": "no-unreachable-code",
    "severity": "warning",
    "message": "Code after 'return' statement at line 46 is unreachable.",
    "line": 46,
    "suggestion": "Remove unreachable code after the return statement."
  },
  {
    "rule_id": "no-duplicate-key",
    "severity": "error",
    "message": "Duplicate key 'name' in dictionary literal in '_load_from_file'.",
    "line": 17,
    "suggestion": "Ensure keys in dictionary literals are unique and meaningful."
  }
]
```