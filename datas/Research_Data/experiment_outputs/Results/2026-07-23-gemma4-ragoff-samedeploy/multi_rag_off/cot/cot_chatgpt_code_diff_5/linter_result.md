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
    "message": "The function 'mysterious_transform' introduces non-deterministic behavior by conditionally applying '.abs()' based on a random roll, making the output unpredictable and untestable.",
    "line": 30,
    "suggestion": "Remove the random condition and apply the transformation consistently or pass it as a parameter."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "error",
    "message": "The function 'aggregate_but_confusing' sorts the result by a random column in a random direction, which is unsuitable for production analysis or reporting.",
    "line": 48,
    "suggestion": "Sort by a specific, meaningful column and direction."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'plot_something' is too generic.",
    "line": 54,
    "suggestion": "Rename to describe the plot content, e.g., 'plot_value_distribution'."
  },
  {
    "rule_id": "software-engineering-standards",
    "severity": "info",
    "message": "The code lacks docstrings for functions, making it difficult to understand the intended input/output types and purpose.",
    "line": 12,
    "suggestion": "Add Google or NumPy style docstrings to all functions."
  }
]
```