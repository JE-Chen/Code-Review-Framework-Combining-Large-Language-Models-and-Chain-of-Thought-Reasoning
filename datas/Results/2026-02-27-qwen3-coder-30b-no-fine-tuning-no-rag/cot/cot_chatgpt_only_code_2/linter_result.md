```json
[
  {
    "rule_id": "no-unexpected-multiline",
    "severity": "warning",
    "message": "Unexpected newline after opening bracket.",
    "line": 27,
    "suggestion": "Add a space after the opening bracket for better readability."
  },
  {
    "rule_id": "no-implicit-coercion",
    "severity": "warning",
    "message": "Avoid implicit type coercion by using explicit conversion.",
    "line": 54,
    "suggestion": "Replace `float(str(avg))` with direct numeric conversion."
  },
  {
    "rule_id": "no-duplicate-key",
    "severity": "error",
    "message": "Duplicate key 'name' detected in dictionary literal.",
    "line": 70,
    "suggestion": "Ensure all keys in the dictionary are unique."
  },
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Unused variable 'text' in function 'loadAndProcessUsers'.",
    "line": 19,
    "suggestion": "Remove unused variable 'text' to improve clarity."
  },
  {
    "rule_id": "no-unsafe-regex",
    "severity": "warning",
    "message": "Potential security risk from unsafe regex usage.",
    "line": 25,
    "suggestion": "Validate and sanitize input before processing."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '0.7' used in conditional logic.",
    "line": 61,
    "suggestion": "Use a named constant for the probability threshold."
  },
  {
    "rule_id": "no-global-assign",
    "severity": "error",
    "message": "Assignment to global variable '_cache' is discouraged.",
    "line": 14,
    "suggestion": "Move cache logic into a dedicated module or class."
  },
  {
    "rule_id": "no-implicit-globals",
    "severity": "warning",
    "message": "Implicit global variable 'DATA_FILE' defined outside function scope.",
    "line": 7,
    "suggestion": "Define constants inside a class or module for encapsulation."
  }
]
```