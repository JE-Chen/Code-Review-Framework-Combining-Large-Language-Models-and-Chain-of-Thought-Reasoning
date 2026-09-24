```json
[
  {
    "rule_id": "software-engineering-standards",
    "severity": "warning",
    "message": "The calculate_discount function contains repetitive conditional logic for 'vip' and 'normal' customer types.",
    "line": 22,
    "suggestion": "Refactor the discount logic into a lookup table or a separate configuration mapping to improve maintainability."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "info",
    "message": "The process_order function recalculates total_price, overriding the value passed during create_order without validating if the original total_price was intended to be a constraint or a pre-calculated value.",
    "line": 68,
    "suggestion": "Ensure the intent of overriding total_price is documented or validate the input total_price against the sum of items."
  },
  {
    "rule_id": "software-engineering-standards",
    "severity": "error",
    "message": "The log_order function uses hasattr to check for 'log' or 'write' methods, which violates the Dependency Inversion Principle and creates a fragile interface.",
    "line": 104,
    "suggestion": "Define a common Logger interface/abstract base class that both FileLogger and ConsoleLogger implement."
  },
  {
    "rule_id": "readability-consistency",
    "severity": "info",
    "message": "Manual string concatenation is used for logging messages.",
    "line": 106,
    "suggestion": "Use f-strings for better readability and performance: f'Order from {order[\"customer_name\"]}'."
  }
]
```