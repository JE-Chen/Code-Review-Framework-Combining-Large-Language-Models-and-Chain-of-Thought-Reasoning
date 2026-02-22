```json
[
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Parameter 'data' in function 'process' is never used after initialization.",
    "line": 38,
    "suggestion": "Remove unused parameter or use it appropriately."
  },
  {
    "rule_id": "no-undef",
    "severity": "error",
    "message": "Variable 'result' is used before being defined in the 'main' function.",
    "line": 44,
    "suggestion": "Assign result after calling process() or ensure proper order of operations."
  },
  {
    "rule_id": "no-unexpected-multiline",
    "severity": "error",
    "message": "Unexpected newline after 'return' keyword may cause syntax errors in some contexts.",
    "line": 44,
    "suggestion": "Ensure consistent formatting around return statements."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '100' used directly in code without explanation.",
    "line": 29,
    "suggestion": "Replace magic number with named constant or variable."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '10' used directly in code without explanation.",
    "line": 27,
    "suggestion": "Replace magic number with named constant or variable."
  },
  {
    "rule_id": "no-empty-blocks",
    "severity": "warning",
    "message": "Empty except block may hide unexpected exceptions.",
    "line": 21,
    "suggestion": "Add logging or handle exception explicitly."
  },
  {
    "rule_id": "no-global-assign",
    "severity": "error",
    "message": "Assignment to global 'CONFIG' object is discouraged.",
    "line": 5,
    "suggestion": "Use local configuration or make CONFIG immutable."
  },
  {
    "rule_id": "no-implicit-globals",
    "severity": "warning",
    "message": "Global variable 'users' in 'UserService' class can lead to side effects.",
    "line": 10,
    "suggestion": "Make instance-specific storage instead of relying on shared state."
  }
]
```