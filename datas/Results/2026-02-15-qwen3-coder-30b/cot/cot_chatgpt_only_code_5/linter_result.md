```json
[
  {
    "rule_id": "function-single-responsibility",
    "severity": "warning",
    "message": "The function 'fn_processTransactions' performs grouping and aggregation logic which could be split into smaller, focused functions.",
    "line": 4,
    "suggestion": "Separate transaction grouping from total calculation into distinct functions."
  },
  {
    "rule_id": "function-single-responsibility",
    "severity": "warning",
    "message": "The function 'print_and_collect' combines printing and data collection, violating single responsibility principle.",
    "line": 43,
    "suggestion": "Split printing and data collection into separate functions."
  },
  {
    "rule_id": "function-single-responsibility",
    "severity": "warning",
    "message": "The function 'calculate_stats' handles sorting, min/max calculation, and average computation without clear separation.",
    "line": 53,
    "suggestion": "Break down statistical computations into individual helper functions."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "The value '100' used in 'check' function is a magic number.",
    "line": 35,
    "suggestion": "Define a named constant for this threshold."
  },
  {
    "rule_id": "no-global-state",
    "severity": "error",
    "message": "Class 'TransactionStore' uses global mutable state via shared class variable 'records'.",
    "line": 24,
    "suggestion": "Use instance variables instead of class variables to avoid unintended side effects."
  },
  {
    "rule_id": "no-duplicate-code",
    "severity": "warning",
    "message": "Duplicate logic exists in 'fn_processTransactions' and 'calculate_stats' for iterating over lists.",
    "line": 4,
    "suggestion": "Refactor repeated list traversal patterns into reusable utilities."
  },
  {
    "rule_id": "inconsistent-naming",
    "severity": "warning",
    "message": "Variable naming inconsistency between snake_case ('lst_transactions') and camelCase ('last_user').",
    "line": 4,
    "suggestion": "Adhere to consistent naming convention throughout the codebase."
  }
]
```