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
    "message": "The process_order function recalculates total_price, overriding the value passed during create_order without validation.",
    "line": 68,
    "suggestion": "Ensure that the initial total_price passed to create_order is either used as a baseline or explicitly documented as being ignored during processing."
  },
  {
    "rule_id": "software-engineering-standards",
    "severity": "error",
    "message": "The log_order function uses hasattr to check for 'log' or 'write' methods, violating the Liskov Substitution Principle and creating a fragile interface.",
    "line": 104,
    "suggestion": "Define a common Logger interface/abstract base class that both FileLogger and ConsoleLogger implement."
  },
  {
    "rule_id": "readability-consistency",
    "severity": "info",
    "message": "Manual string concatenation used for logging messages.",
    "line": 106,
    "suggestion": "Use f-strings for better readability and performance: f'Order from {order[\"customer_name\"]}'."
  }
]
```