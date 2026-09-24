```json
[
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Parameter 'now' is defined but not used in function 'process_order'.",
    "line": 30,
    "suggestion": "Remove unused parameter 'now' or use it in the function."
  },
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Variable 'total' is assigned but never used after the loop in function 'process_order'.",
    "line": 48,
    "suggestion": "Remove unused variable 'total' or use it appropriately."
  },
  {
    "rule_id": "no-duplicate-case",
    "severity": "error",
    "message": "Duplicate case condition detected in 'calculate_discount' function.",
    "line": 28,
    "suggestion": "Ensure each case in conditional logic is unique or refactor to avoid duplication."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '1000' found in 'calculate_discount'. Consider defining as a named constant.",
    "line": 19,
    "suggestion": "Define '1000' as a named constant like MAX_VIP_THRESHOLD."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '500' found in 'calculate_discount'. Consider defining as a named constant.",
    "line": 22,
    "suggestion": "Define '500' as a named constant like MIN_VIP_THRESHOLD."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '1200' found in 'main'. Consider defining as a named constant.",
    "line": 74,
    "suggestion": "Define '1200' as a named constant like LAPTOP_PRICE."
  },
  {
    "rule_id": "no-duplicate-code",
    "severity": "warning",
    "message": "Similar logic for printing order details exists in both 'OrderPrinter' and 'main'.",
    "line": 57,
    "suggestion": "Refactor duplicated logic into a shared utility function."
  },
  {
    "rule_id": "no-implicit-globals",
    "severity": "warning",
    "message": "Global variable 'order' is modified within 'process_order'.",
    "line": 41,
    "suggestion": "Avoid modifying global state; consider returning updated data instead."
  },
  {
    "rule_id": "no-undefined-variables",
    "severity": "error",
    "message": "Undefined variable 'discount_rate' may be referenced before assignment.",
    "line": 43,
    "suggestion": "Ensure all variables are initialized before usage."
  },
  {
    "rule_id": "no-unreachable-code",
    "severity": "warning",
    "message": "Unreachable code after return statement in 'process_order'.",
    "line": 50,
    "suggestion": "Move unreachable code outside the function or restructure logic."
  }
]
```