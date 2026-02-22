```json
[
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Variable 'now' is defined but not used in function 'process_order'.",
    "line": 31,
    "suggestion": "Remove unused parameter 'now' or use it in the function."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '1000' used in discount calculation; consider defining as a named constant.",
    "line": 19,
    "suggestion": "Define constants like MIN_VIP_PURCHASE or MIN_NORMAL_PURCHASE for clarity."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '500' used in discount calculation; consider defining as a named constant.",
    "line": 22,
    "suggestion": "Define constants like MIN_VIP_PURCHASE or MIN_NORMAL_PURCHASE for clarity."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '100' used in discount calculation; consider defining as a named constant.",
    "line": 28,
    "suggestion": "Define constants like MIN_NORMAL_PURCHASE or MIN_DISCOUNT_THRESHOLD for clarity."
  },
  {
    "rule_id": "no-duplicate-code",
    "severity": "warning",
    "message": "Duplicate conditional logic in calculating discounts for 'vip' and 'normal' customers.",
    "line": 15,
    "suggestion": "Refactor discount logic into a helper function to reduce duplication."
  },
  {
    "rule_id": "no-implicit-dependencies",
    "severity": "warning",
    "message": "The 'process_order' function modifies the input order dictionary directly without explicit copying.",
    "line": 37,
    "suggestion": "Consider making a copy of the input before modifying to avoid side effects."
  },
  {
    "rule_id": "no-verbose-print",
    "severity": "warning",
    "message": "Use of print() statements instead of proper logging for error messages in 'process_order'.",
    "line": 33,
    "suggestion": "Replace print() calls with logging module for better control over output."
  },
  {
    "rule_id": "no-verbose-print",
    "severity": "warning",
    "message": "Use of print() statements instead of proper logging for debug information in 'process_order'.",
    "line": 46,
    "suggestion": "Replace print() calls with logging module for better control over output."
  },
  {
    "rule_id": "no-type-checking",
    "severity": "warning",
    "message": "No type hints provided for function parameters or return types.",
    "line": 1,
    "suggestion": "Add type hints for improved readability and static analysis support."
  },
  {
    "rule_id": "no-nested-conditionals",
    "severity": "warning",
    "message": "Deeply nested conditional blocks in discount logic can reduce readability.",
    "line": 14,
    "suggestion": "Simplify nesting by restructuring conditionals or extracting logic into functions."
  }
]
```