[
  {
    "rule_id": "misleading-name",
    "severity": "warning",
    "message": "Variable 'dataFrameLike' is misleading as it represents a simple list of lists, not a DataFrame-like structure.",
    "line": 6,
    "suggestion": "Rename to 'sample_data' or 'raw_data' for accuracy."
  },
  {
    "rule_id": "no-global-state",
    "severity": "warning",
    "message": "Extensive use of global variables reduces modularity and testability.",
    "line": 6,
    "suggestion": "Refactor to use dependency injection or object-oriented design."
  },
  {
    "rule_id": "redundant-calculation",
    "severity": "warning",
    "message": "Mean is calculated twice for identical data without purpose.",
    "line": 26,
    "suggestion": "Remove redundant calculation of 'meanNumAgain'."
  },
  {
    "rule_id": "inefficient-category-count",
    "severity": "warning",
    "message": "Category counting uses O(n^2) complexity via nested .count() calls.",
    "line": 34,
    "suggestion": "Replace with O(n) approach using collections.Counter."
  },
  {
    "rule_id": "stale-data-in-cache",
    "severity": "error",
    "message": "Result cache retains stale values when analysis conditions fail.",
    "line": 17,
    "suggestion": "Clear cache at function start or reset keys explicitly."
  },
  {
    "rule_id": "missing-docstring",
    "severity": "info",
    "message": "No documentation provided for functions.",
    "line": 12,
    "suggestion": "Add docstrings explaining function purpose and behavior."
  }
]