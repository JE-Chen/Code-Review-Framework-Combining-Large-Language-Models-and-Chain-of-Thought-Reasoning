[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'fn_processTransactions' uses non-standard prefix 'fn_'. Prefer descriptive snake_case without prefixes.",
    "line": 3,
    "suggestion": "Rename to 'process_transactions'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Parameter 'lst_transactions' uses non-standard prefix 'lst_'. Prefer descriptive names without prefixes.",
    "line": 3,
    "suggestion": "Rename to 'transactions'."
  },
  {
    "rule_id": "logic-bug",
    "severity": "error",
    "message": "Function returns [0] for empty input instead of empty list. Empty input handling is missing.",
    "line": 23,
    "suggestion": "Return empty list when input is empty."
  },
  {
    "rule_id": "input-validation",
    "severity": "error",
    "message": "Statistics functions called on potentially empty 'values' list. May raise ValueError.",
    "line": 38,
    "suggestion": "Validate 'values' is non-empty before calling statistics functions."
  },
  {
    "rule_id": "design-flaw",
    "severity": "warning",
    "message": "Class-level 'records' shared across instances. Causes unintended state sharing.",
    "line": 47,
    "suggestion": "Use instance-level attribute for 'records' instead of class-level."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "'check' function name is too generic. Does not convey purpose (amount > 100 check).",
    "line": 65,
    "suggestion": "Rename to 'is_big_amount' for clarity."
  },
  {
    "rule_id": "input-validation",
    "severity": "warning",
    "message": "Dictionary keys 'user' and 'amount' accessed directly without validation. May cause KeyError.",
    "line": 73,
    "suggestion": "Use .get() or validate keys before access."
  },
  {
    "rule_id": "single-responsibility",
    "severity": "warning",
    "message": "Function 'print_and_collect' has side effect (print) and returns value. Violates single responsibility.",
    "line": 81,
    "suggestion": "Separate printing and collection into distinct functions."
  },
  {
    "rule_id": "logic-bug",
    "severity": "error",
    "message": "Function fails on empty input due to index access on empty list ('temp[0]').",
    "line": 93,
    "suggestion": "Add empty input check before accessing list elements."
  }
]