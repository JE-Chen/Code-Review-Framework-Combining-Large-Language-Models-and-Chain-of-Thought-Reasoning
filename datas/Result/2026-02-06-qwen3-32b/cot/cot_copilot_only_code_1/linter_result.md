[
  {
    "rule_id": "unused-parameters",
    "severity": "warning",
    "message": "Function doSomething has unused parameters: g, h, i, j.",
    "line": 1,
    "suggestion": "Remove unused parameters or use them meaningfully."
  },
  {
    "rule_id": "deep-nesting",
    "severity": "warning",
    "message": "Function doSomething has deeply nested conditionals (4 levels).",
    "line": 3,
    "suggestion": "Refactor to reduce nesting using guard clauses or helper functions."
  },
  {
    "rule_id": "inconsistent-return-type",
    "severity": "error",
    "message": "Function doSomething returns float in some branches and integer in others.",
    "line": 7,
    "suggestion": "Ensure consistent return types by using integer division or converting to integer."
  },
  {
    "rule_id": "magic-number",
    "severity": "warning",
    "message": "Magic number 999999 used in doSomething.",
    "line": 9,
    "suggestion": "Define a constant for the error value."
  },
  {
    "rule_id": "global-mutable-state",
    "severity": "warning",
    "message": "Mutable global list 'dataList' is used. Avoid global state.",
    "line": 24,
    "suggestion": "Encapsulate dataList within a class or pass it as a parameter."
  },
  {
    "rule_id": "avoid-indexing",
    "severity": "warning",
    "message": "Using index-based iteration in processData instead of direct value iteration.",
    "line": 28,
    "suggestion": "Replace with 'for value in dataList: ...'."
  }
]