[
  {
    "rule_id": "bad-function-name",
    "severity": "warning",
    "message": "Function name 'load_data_but_not_really' is misleading as it generates random data instead of loading from a file.",
    "line": 12,
    "suggestion": "Rename to 'generate_random_data' or similar to accurately describe the function's purpose."
  },
  {
    "rule_id": "bad-function-name",
    "severity": "warning",
    "message": "Function name 'mysterious_transform' is non-descriptive and fails to convey the transformation logic.",
    "line": 26,
    "suggestion": "Rename to a descriptive name such as 'filter_and_square_values'."
  },
  {
    "rule_id": "bad-function-name",
    "severity": "warning",
    "message": "Function name 'aggregate_but_confusing' is misleading and does not reflect the non-deterministic sorting.",
    "line": 37,
    "suggestion": "Rename to 'aggregate_and_sort' and remove randomness or make it configurable."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "warning",
    "message": "Function is missing a docstring to explain its purpose, parameters, and return values.",
    "line": 12,
    "suggestion": "Add a docstring describing the function's behavior and inputs."
  },
  {
    "rule_id": "non-deterministic-behavior",
    "severity": "warning",
    "message": "Function 'mysterious_transform' contains non-deterministic behavior via random choice in condition.",
    "line": 29,
    "suggestion": "Make the behavior deterministic by removing randomness or using a fixed seed."
  },
  {
    "rule_id": "non-deterministic-behavior",
    "severity": "warning",
    "message": "Function 'aggregate_but_confusing' uses random column and order for sorting, making output non-reproducible.",
    "line": 49,
    "suggestion": "Use a deterministic sort key or allow the sort order to be specified as a parameter."
  }
]