```json
[
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Variable 'report' is assigned but never used after reassignment.",
    "line": 58,
    "suggestion": "Remove the unused assignment or use the variable."
  },
  {
    "rule_id": "no-duplicate-case",
    "severity": "error",
    "message": "Duplicate case value 'text' found in switch statement.",
    "line": 75,
    "suggestion": "Ensure each case has a unique value or remove duplicates."
  },
  {
    "rule_id": "no-undef",
    "severity": "error",
    "message": "Undefined variable 'fmt' in conditional block.",
    "line": 74,
    "suggestion": "Ensure all variables are properly declared before use."
  },
  {
    "rule_id": "no-unreachable",
    "severity": "warning",
    "message": "Unreachable code detected after return statement.",
    "line": 83,
    "suggestion": "Remove unreachable code or restructure logic."
  },
  {
    "rule_id": "no-console",
    "severity": "warning",
    "message": "Unexpected console output.",
    "line": 21,
    "suggestion": "Replace console.log with proper logging mechanism."
  },
  {
    "rule_id": "no-implicit-globals",
    "severity": "error",
    "message": "Global variable 'CONFIG' is not declared with 'const', 'let', or 'var'.",
    "line": 3,
    "suggestion": "Declare 'CONFIG' using appropriate keyword like 'const'."
  },
  {
    "rule_id": "no-var",
    "severity": "warning",
    "message": "Use of 'var' instead of 'const' or 'let'.",
    "line": 56,
    "suggestion": "Replace 'var' with 'const' or 'let' for better scoping."
  }
]
```