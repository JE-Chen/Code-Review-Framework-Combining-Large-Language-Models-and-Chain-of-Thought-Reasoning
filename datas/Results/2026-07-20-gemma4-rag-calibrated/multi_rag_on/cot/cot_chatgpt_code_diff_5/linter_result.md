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
    "rule_id": "mutate-input-argument",
    "severity": "error",
    "message": "Function 'mysterious_transform' modifies the input DataFrame 'df' in-place by adding 'value_squared' and potentially modifying 'value'.",
    "line": 27,
    "suggestion": "Create a copy of the DataFrame using 'df = df.copy()' at the start of the function to avoid side effects for the caller."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'aggregate_but_confusing' is not descriptive and lacks semantic clarity.",
    "line": 36,
    "suggestion": "Rename to something descriptive, e.g., 'aggregate_category_metrics'."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "warning",
    "message": "The sorting logic in 'aggregate_but_confusing' uses random choices for both the column and the order, making the output non-deterministic and difficult to test.",
    "line": 48,
    "suggestion": "Use a fixed column and order, or pass them as arguments to the function."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'plot_something' is too generic and not descriptive.",
    "line": 54,
    "suggestion": "Rename to reflect the plot content, e.g., 'plot_value_distribution'."
  }
]
```