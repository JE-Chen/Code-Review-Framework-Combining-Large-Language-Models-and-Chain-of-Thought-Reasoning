```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'fn_processTransactions' does not follow Python's snake_case naming convention.",
    "line": 4,
    "suggestion": "Rename to 'process_transactions'."
  },
  {
    "rule_id": "inconsistent-return-types",
    "severity": "warning",
    "message": "The 'Analyzer.analyze' method returns different types (float/int from statistics.mean/median vs int from max) depending on the mode, which can lead to unpredictable behavior for callers.",
    "line": 32,
    "suggestion": "Ensure a consistent return type, such as casting all results to float."
  },
  {
    "rule_id": "shared-mutable-state",
    "severity": "error",
    "message": "Class attribute 'records' in 'TransactionStore' is a shared mutable list. This creates hidden coupling and makes the class non-thread-safe and difficult to test in isolation.",
    "line": 47,
    "suggestion": "Move 'records' to the __init__ method as an instance attribute (self.records)."
  },
  {
    "rule_id": "magic-number",
    "severity": "info",
    "message": "Hard-coded date '2026-01-01' used as a default value.",
    "line": 73,
    "suggestion": "Define this as a named constant at the top of the module."
  },
  {
    "rule_id": "magic-number",
    "severity": "info",
    "message": "Hard-coded threshold '100' used in 'check' function.",
    "line": 67,
    "suggestion": "Define this as a named constant (e.g., TRANSACTION_THRESHOLD)."
  },
  {
    "rule_id": "unnecessary-work",
    "severity": "warning",
    "message": "The loop in 'calculate_stats' manually copies elements from 'numbers' to 'temp', which is redundant.",
    "line": 91,
    "suggestion": "Use 'temp = sorted(numbers)' to create a sorted copy in one step."
  },
  {
    "rule_id": "boundary-condition",
    "severity": "error",
    "message": "Potential ZeroDivisionError in 'calculate_stats' if 'numbers' list is empty.",
    "line": 98,
    "suggestion": "Add a check for 'if not temp: return {}' or handle the empty list case."
  }
]
```