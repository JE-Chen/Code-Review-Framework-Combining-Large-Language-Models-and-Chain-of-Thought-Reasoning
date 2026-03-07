```json
[
  {
    "rule_id": "no-global-assign",
    "severity": "error",
    "message": "Assignment to global variable 'GLOBAL_THING' detected. Global state should be avoided.",
    "line": 14,
    "suggestion": "Avoid modifying global variables. Consider returning the value or using a class to encapsulate state."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '37' used. Replace with a named constant for clarity.",
    "line": 17,
    "suggestion": "Define 'MAGIC' as a named constant at the top of the module for better readability."
  },
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Unused import 'sys'. Remove if not needed.",
    "line": 7,
    "suggestion": "Remove unused import 'sys' from the imports."
  },
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Unused import 'time'. Remove if not needed.",
    "line": 7,
    "suggestion": "Remove unused import 'time' from the imports."
  },
  {
    "rule_id": "no-undef",
    "severity": "error",
    "message": "Undefined variable 'df' in exception handler. Potential reference error.",
    "line": 49,
    "suggestion": "Ensure all variables referenced in exception blocks are properly initialized before use."
  },
  {
    "rule_id": "no-unsafe-assignment",
    "severity": "warning",
    "message": "Using 'lambda' inside 'apply' may cause performance issues. Consider vectorization.",
    "line": 32,
    "suggestion": "Use vectorized operations instead of lambda functions when possible for better performance."
  },
  {
    "rule_id": "no-unsafe-assignment",
    "severity": "warning",
    "message": "Using 'lambda' inside 'apply' may cause performance issues. Consider vectorization.",
    "line": 43,
    "suggestion": "Use vectorized operations instead of lambda functions when possible for better performance."
  },
  {
    "rule_id": "no-unsafe-assignment",
    "severity": "warning",
    "message": "Using 'lambda' inside 'apply' may cause performance issues. Consider vectorization.",
    "line": 53,
    "suggestion": "Use vectorized operations instead of lambda functions when possible for better performance."
  },
  {
    "rule_id": "no-unsafe-assignment",
    "severity": "warning",
    "message": "Using 'lambda' inside 'apply' may cause performance issues. Consider vectorization.",
    "line": 59,
    "suggestion": "Use vectorized operations instead of lambda functions when possible for better performance."
  },
  {
    "rule_id": "no-duplicate-key",
    "severity": "error",
    "message": "Duplicate key 'col_one' in DataFrame construction. This will overwrite previous values.",
    "line": 27,
    "suggestion": "Check that column names in DataFrame constructor are unique and intended."
  },
  {
    "rule_id": "no-unreachable-code",
    "severity": "warning",
    "message": "Unreachable code after 'return' statement. Remove unreachable lines.",
    "line": 68,
    "suggestion": "Ensure no code exists after a return statement in the same function block."
  },
  {
    "rule_id": "no-implicit-globals",
    "severity": "error",
    "message": "Global variable 'STRANGE_CACHE' used without explicit declaration. Should be declared at module level.",
    "line": 16,
    "suggestion": "Explicitly declare 'STRANGE_CACHE' as a global variable at the top of the module."
  }
]
```