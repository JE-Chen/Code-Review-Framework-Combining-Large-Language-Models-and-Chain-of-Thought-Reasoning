```json
[
  {
    "rule_id": "software-engineering-standards",
    "severity": "warning",
    "message": "The 'calculate_discount' function contains repetitive conditional logic for 'vip' and 'normal' customer types.",
    "line": 23,
    "suggestion": "Refactor the discount logic into a lookup table or a separate configuration mapping to improve maintainability."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "info",
    "message": "The 'process_order' function overwrites 'order[\"total_price\"]' based on the sum of items, ignoring the 'total_price' value passed during 'create_order'.",
    "line": 73,
    "suggestion": "Ensure this behavior is intentional; otherwise, validate the passed total against the calculated sum."
  },
  {
    "rule_id": "software-engineering-standards",
    "severity": "error",
    "message": "The 'log_order' function uses 'hasattr' to check for 'log' or 'write' methods, which violates the Dependency Inversion Principle and creates a fragile interface.",
    "line": 112,
    "suggestion": "Define a common Logger interface (Abstract Base Class) that both FileLogger and ConsoleLogger implement."
  },
  {
    "rule_id": "readability-consistency",
    "severity": "info",
    "message": "The 'process_order' function uses 'print' statements for error handling ('No items', 'Empty order') instead of raising exceptions or using a logging framework.",
    "line": 56,
    "suggestion": "Replace print statements with appropriate exceptions (e.g., ValueError) or a logger."
  }
]
```