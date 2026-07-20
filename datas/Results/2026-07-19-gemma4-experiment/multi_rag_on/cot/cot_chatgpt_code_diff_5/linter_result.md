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
    "line": 25,
    "suggestion": "Rename to reflect the actual transformation logic, e.g., 'filter_and_square_values'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'aggregate_but_confusing' is not descriptive and lacks semantic clarity.",
    "line": 36,
    "suggestion": "Rename to reflect the aggregation purpose, e.g., 'aggregate_category_metrics'."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "error",
    "message": "The function 'mysterious_transform' modifies the input DataFrame in-place (adding 'value_squared' and potentially modifying 'value') before returning a filtered copy. This can lead to unexpected side effects for the caller.",
    "line": 26,
    "suggestion": "Create a copy of the DataFrame using 'df = df.copy()' at the start of the function."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "warning",
    "message": "The sorting logic in 'aggregate_but_confusing' uses random choices for both the column and the order, making the output non-deterministic and difficult to test or verify.",
    "line": 48,
    "suggestion": "Use a fixed column and order, or pass them as arguments to the function."
  },
  {
    "rule_id": "naming-convention",
    "severity": "info",
    "message": "Function name 'plot_something' is too generic.",
    "line": 54,
    "suggestion": "Rename to describe the plot content, e.g., 'plot_value_distribution'."
  }
]
```