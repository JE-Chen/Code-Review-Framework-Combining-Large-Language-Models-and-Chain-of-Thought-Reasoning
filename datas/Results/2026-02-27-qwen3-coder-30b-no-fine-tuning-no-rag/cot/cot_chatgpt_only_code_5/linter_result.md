```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'fn_processTransactions' does not follow snake_case naming convention.",
    "line": 4,
    "suggestion": "Rename 'fn_processTransactions' to 'process_transactions'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable name 'lst_transactions' does not follow snake_case naming convention.",
    "line": 4,
    "suggestion": "Rename 'lst_transactions' to 'list_transactions' or 'transactions'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Class name 'TransactionStore' does not follow PascalCase naming convention.",
    "severity": "warning",
    "message": "Class name 'TransactionStore' does not follow PascalCase naming convention.",
    "line": 24,
    "suggestion": "Rename 'TransactionStore' to 'TransactionStore' (already PascalCase)."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'check' is too generic and lacks context.",
    "line": 48,
    "suggestion": "Rename 'check' to something more descriptive like 'is_big_amount'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable name 'temp' is not descriptive enough.",
    "line": 62,
    "suggestion": "Rename 'temp' to 'sorted_numbers' or similar."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '100' used in function 'check'.",
    "line": 49,
    "suggestion": "Replace magic number '100' with a named constant like MAX_AMOUNT_THRESHOLD."
  },
  {
    "rule_id": "no-duplicate-code",
    "severity": "warning",
    "message": "Duplicate code block in 'calculate_stats' function that can be extracted into a helper function.",
    "line": 62,
    "suggestion": "Extract sorting and min/max/avg calculation into a reusable utility function."
  },
  {
    "rule_id": "no-global-state",
    "severity": "error",
    "message": "Class 'TransactionStore' uses a mutable global state (records).",
    "line": 25,
    "suggestion": "Use instance variables instead of class-level ones to avoid shared state issues."
  },
  {
    "rule_id": "no-implicit-boolean-check",
    "severity": "warning",
    "message": "Inconsistent use of explicit boolean checks ('if x == 0.0') vs implicit checks.",
    "line": 19,
    "suggestion": "Use 'if not x:' for checking falsy values instead of comparing with 0.0."
  },
  {
    "rule_id": "no-unreachable-code",
    "severity": "warning",
    "message": "Unreachable code after 'return' statement in 'Analyzer.analyze'.",
    "line": 31,
    "suggestion": "Remove redundant condition checks after returning from previous branches."
  },
  {
    "rule_id": "no-unnecessary-pass",
    "severity": "info",
    "message": "No pass statements required here.",
    "line": 38,
    "suggestion": "Remove any unnecessary pass statements."
  },
  {
    "rule_id": "no-side-effects",
    "severity": "error",
    "message": "The 'print_and_collect' function has side effects by printing to console.",
    "line": 52,
    "suggestion": "Separate printing logic from collection logic to improve testability."
  },
  {
    "rule_id": "no-hardcoded-values",
    "severity": "warning",
    "message": "Hardcoded date value '2026-01-01' used as default.",
    "line": 57,
    "suggestion": "Define a constant for this default date to allow easy modification."
  }
]
```