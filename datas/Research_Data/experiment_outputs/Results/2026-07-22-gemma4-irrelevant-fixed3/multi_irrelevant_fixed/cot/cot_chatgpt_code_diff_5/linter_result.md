```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'load_data_but_not_really' is not descriptive and lacks semantic clarity.",
    "line": 12,
    "suggestion": "Rename to something descriptive, e.g., 'generate_sample_data'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'mysterious_transform' is not descriptive and lacks semantic clarity.",
    "line": 26,
    "suggestion": "Rename to reflect the actual transformation logic, e.g., 'filter_and_square_values'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'aggregate_but_confusing' is not descriptive and lacks semantic clarity.",
    "line": 37,
    "suggestion": "Rename to reflect the aggregation purpose, e.g., 'aggregate_category_metrics'."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "error",
    "message": "The function 'aggregate_but_confusing' uses random.choice for sorting columns and order, leading to non-deterministic and unpredictable output.",
    "line": 51,
    "suggestion": "Use a fixed column name and a consistent sorting order."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "warning",
    "message": "The transformation in 'mysterious_transform' conditionally applies .abs() based on a random float, making the data pipeline non-reproducible.",
    "line": 30,
    "suggestion": "Remove random logic from data transformation to ensure consistency."
  },
  {
    "rule_id": "software-engineering-standards",
    "severity": "info",
    "message": "The function 'plot_something' contains a hardcoded label 'value_squared (maybe)' which is ambiguous.",
    "line": 72,
    "suggestion": "Use a clear, definitive label for the Y-axis."
  }
]
```