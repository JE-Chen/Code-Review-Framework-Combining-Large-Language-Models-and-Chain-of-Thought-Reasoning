```json
[
  {
    "rule_id": "deeply-nested-conditional",
    "severity": "warning",
    "message": "Deeply nested conditional logic in calculate_discount reduces readability and increases cognitive load.",
    "line": 23,
    "suggestion": "Refactor the discount logic into a lookup table or use guard clauses to flatten the structure."
  },
  {
    "rule_id": "magic-numbers",
    "severity": "info",
    "message": "Hard-coded constants (1000, 500, 0.2, 0.1, etc.) are used for discount thresholds and rates.",
    "line": 24,
    "suggestion": "Define these values as named constants at the module level (e.g., VIP_HIGH_THRESHOLD = 1000)."
  },
  {
    "rule_id": "modify-input-argument",
    "severity": "warning",
    "message": "The function process_order modifies the input 'order' dictionary directly, which can lead to surprising side effects for the caller.",
    "line": 68,
    "suggestion": "Create a copy of the order dictionary or return a new object containing the processed results."
  },
  {
    "rule_id": "implicit-truthiness",
    "severity": "info",
    "message": "Implicit truthiness used to check for empty items list.",
    "line": 52,
    "suggestion": "Use an explicit comparison such as 'if len(order[\"items\"]) == 0:' (though already present, the logic could be simplified to a guard clause)."
  },
  {
    "rule_id": "single-responsibility",
    "severity": "warning",
    "message": "process_order handles multiple responsibilities: calculating totals, applying discounts, and logging/printing via the verbose flag.",
    "line": 47,
    "suggestion": "Split the function into separate functions for total calculation and order processing."
  },
  {
    "rule_id": "predictable-interface",
    "severity": "warning",
    "message": "log_order relies on checking for different method names ('log' vs 'write') on the logger object, creating an unpredictable interface.",
    "line": 98,
    "suggestion": "Define a common Logger interface/abstract base class that enforces a single method name (e.g., 'log')."
  }
]
```