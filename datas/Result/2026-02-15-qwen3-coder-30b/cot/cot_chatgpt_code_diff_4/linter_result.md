```json
[
  {
    "rule_id": "no-global-assign",
    "severity": "error",
    "message": "Unexpected assignment to global variable 'CONN'. Global variables should not be reassigned.",
    "line": 7,
    "suggestion": "Use a local connection or ensure this is intentional and documented."
  },
  {
    "rule_id": "no-global-assign",
    "severity": "error",
    "message": "Unexpected assignment to global variable 'CURSOR'. Global variables should not be reassigned.",
    "line": 8,
    "suggestion": "Use a local cursor or ensure this is intentional and documented."
  },
  {
    "rule_id": "no-useless-escape",
    "severity": "warning",
    "message": "Unnecessary escape sequence '\\(' in string literal.",
    "line": 23,
    "suggestion": "Remove unnecessary escape sequences."
  },
  {
    "rule_id": "no-duplicate-key",
    "severity": "error",
    "message": "Duplicate key 'ts' in object literal.",
    "line": 25,
    "suggestion": "Ensure unique keys in object literals."
  },
  {
    "rule_id": "no-unreachable",
    "severity": "warning",
    "message": "Unreachable code after return statement.",
    "line": 39,
    "suggestion": "Remove unreachable code."
  },
  {
    "rule_id": "no-empty-blocks",
    "severity": "warning",
    "message": "Empty block statement.",
    "line": 39,
    "suggestion": "Add meaningful logic or remove the block."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number: 3 used directly in code.",
    "line": 15,
    "suggestion": "Replace magic number with named constant."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number: 5 used directly in code.",
    "line": 19,
    "suggestion": "Replace magic number with named constant."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number: 0.2 used directly in code.",
    "line": 47,
    "suggestion": "Replace magic number with named constant."
  },
  {
    "rule_id": "no-var",
    "severity": "warning",
    "message": "Use of 'var' instead of 'let' or 'const'.",
    "line": 21,
    "suggestion": "Prefer 'let' or 'const' over 'var'."
  },
  {
    "rule_id": "no-implicit-globals",
    "severity": "error",
    "message": "Implicit global variable 'CONN' declared outside of any function.",
    "line": 7,
    "suggestion": "Declare global variables explicitly using 'var', 'let', or 'const'."
  },
  {
    "rule_id": "no-implicit-globals",
    "severity": "error",
    "message": "Implicit global variable 'CURSOR' declared outside of any function.",
    "line": 8,
    "suggestion": "Declare global variables explicitly using 'var', 'let', or 'const'."
  }
]
```