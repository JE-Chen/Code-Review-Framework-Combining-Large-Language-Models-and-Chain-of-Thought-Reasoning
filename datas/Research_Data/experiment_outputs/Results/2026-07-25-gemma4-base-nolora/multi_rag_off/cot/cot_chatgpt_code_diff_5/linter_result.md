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
    "suggestion": "Rename to something descriptive, e.g., 'aggregate_category_metrics'."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "error",
    "message": "The function 'mysterious_transform' modifies the input DataFrame in-place ('df[\"value_squared\"] = ...') but also returns a filtered copy. This creates inconsistent behavior regarding side effects.",
    "line": 27,
    "suggestion": "Use 'df = df.copy()' at the start of the function to avoid mutating the original DataFrame."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "error",
    "message": "The sorting logic in 'aggregate_but_confusing' uses 'random.choice' for both the column and the direction, making the output non-deterministic and unsuitable for a standard analysis pipeline.",
    "line": 49,
    "suggestion": "Use a fixed column name and a consistent sorting order."
  },
  {
    "rule_id": "software-engineering-standard",
    "severity": "info",
    "message": "The use of 'random.random() > 0.5' inside 'mysterious_transform' introduces non-deterministic logic into the data processing pipeline.",
    "line": 30,
    "suggestion": "Remove random branching or make it a configurable parameter of the function."
  }
]
```