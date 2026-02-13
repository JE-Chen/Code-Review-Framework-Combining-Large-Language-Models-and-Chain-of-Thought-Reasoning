```json
[
  {
    "rule_id": "too-nested-conditions",
    "severity": "error",
    "message": "Deeply nested if-else structure reduces readability and increases cognitive load.",
    "line": 10,
    "suggestion": "Refactor complex conditionals into smaller functions or use guard clauses."
  },
  {
    "rule_id": "hard-coded-constant",
    "severity": "error",
    "message": "Hard-coded value 999999 in doSomething() reduces maintainability and clarity.",
    "line": 14,
    "suggestion": "Replace with a computed value or document the rationale."
  },
  {
    "rule_id": "reused-variable-name",
    "severity": "warning",
    "message": "Variable 'result' is reused in multiple contexts without clear renaming.",
    "line": 8,
    "suggestion": "Rename to 'computedValue' for clarity and consistency."
  },
  {
    "rule_id": "unhandled-edge-case",
    "severity": "warning",
    "message": "d == 0 in doSomething() returns 999999 without handling.",
    "line": 12,
    "suggestion": "Add explicit fallback logic for d == 0."
  },
  {
    "rule_id": "inconsistent-return-type",
    "severity": "warning",
    "message": "Multiple return types (int, str) in doSomething() reduce caller predictability.",
    "line": 16,
    "suggestion": "Use a single return type and document behavior."
  },
  {
    "rule_id": "unused-variable",
    "severity": "warning",
    "message": "Variables like 'x' and 'y' are not used in main() and processData()",
    "line": 19,
    "suggestion": "Remove unused variables or use them in logical contexts."
  },
  {
    "rule_id": "implicit-parameters",
    "severity": "warning",
    "message": "Function parameters are not clearly documented or used in logic.",
    "line": 12,
    "suggestion": "Add docstrings and parameter usage examples."
  }
]
```