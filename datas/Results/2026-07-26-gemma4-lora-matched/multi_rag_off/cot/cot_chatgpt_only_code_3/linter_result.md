```json
[
  {
    "rule_id": "software-engineering-standards",
    "severity": "warning",
    "message": "The 'calculate_discount' function contains deeply nested if-elif-else blocks that are difficult to maintain and scale.",
    "line": 21,
    "suggestion": "Use a lookup table (dictionary) to map customer types and price thresholds to discount rates."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "info",
    "message": "The 'process_order' function recalculates 'total_price' based on items, but 'create_order' also accepts 'total_price' as an argument, creating a potential source of truth conflict.",
    "line": 54,
    "suggestion": "Remove 'total_price' from 'create_order' arguments and let 'process_order' be the sole authority for calculating the total."
  },
  {
    "rule_id": "software-engineering-standards",
    "severity": "error",
    "message": "The 'log_order' function uses 'hasattr' to check for 'log' or 'write' methods, which violates the Dependency Inversion Principle and creates an unstable interface.",
    "line": 104,
    "suggestion": "Define a common Logger interface/abstract base class that both FileLogger and ConsoleLogger implement."
  },
  {
    "rule_id": "readability-consistency",
    "severity": "info",
    "message": "The 'OrderPrinter' class contains a single method and does not maintain any state, making it an unnecessary class.",
    "line": 88,
    "suggestion": "Convert 'print_order' into a standalone function."
  }
]
```