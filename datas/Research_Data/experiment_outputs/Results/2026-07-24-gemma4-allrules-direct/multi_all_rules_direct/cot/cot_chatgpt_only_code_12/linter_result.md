```json
[
  {
    "rule_id": "naming-conventions",
    "severity": "warning",
    "message": "Function name 'do_everything_and_nothing_at_once' is not descriptive and does not reflect the function's intent.",
    "line": 13,
    "suggestion": "Rename the function to describe its actual purpose (e.g., 'analyze_and_plot_data')."
  },
  {
    "rule_id": "mutable-default-arguments",
    "severity": "error",
    "message": "Avoid using mutable default arguments (y=[], z={}) in function definitions. These are evaluated once at definition time and shared across calls.",
    "line": 13,
    "suggestion": "Use 'y=None, z=None' and initialize them inside the function."
  },
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "Use of 'global GLOBAL_THING' introduces hidden coupling and makes the function harder to test and reason about.",
    "line": 14,
    "suggestion": "Pass state explicitly as arguments or return the value to the caller."
  },
  {
    "rule_id": "magic-numbers",
    "severity": "info",
    "message": "Hard-coded constants (10, 200, 2, 5, 1.5, 3, 0.01) are used throughout the logic.",
    "line": 16,
    "suggestion": "Define these as named constants at the top of the module to improve maintainability."
  },
  {
    "rule_id": "broad-exception-handling",
    "severity": "error",
    "message": "Bare 'except:' clause catches all exceptions, including SystemExit and KeyboardInterrupt, which can hide bugs.",
    "line": 27,
    "suggestion": "Catch a specific exception type (e.g., 'ValueError')."
  },
  {
    "rule_id": "single-responsibility-principle",
    "severity": "warning",
    "message": "The function performs data generation, transformation, statistical analysis, caching, and visualization. It has too many responsibilities.",
    "line": 13,
    "suggestion": "Split the function into smaller, focused functions (e.g., 'generate_data', 'calculate_metrics', 'plot_results')."
  },
  {
    "rule_id": "performance-bottleneck",
    "severity": "warning",
    "message": "Using 'df.iloc[i]' inside a loop to iterate over a DataFrame is highly inefficient.",
    "line": 46,
    "suggestion": "Use vectorized pandas operations or 'df.itertuples()' / 'df.apply()'."
  },
  {
    "rule_id": "broad-exception-handling",
    "severity": "error",
    "message": "Catching 'Exception' is too broad and may mask unexpected runtime errors.",
    "line": 51,
    "suggestion": "Catch specific exceptions that are expected during the summation process."
  },
  {
    "rule_id": "shared-mutable-state",
    "severity": "warning",
    "message": "Modifying the module-level 'STRANGE_CACHE' dictionary creates shared mutable state.",
    "line": 60,
    "suggestion": "Encapsulate the cache in a class or pass it as an argument."
  },
  {
    "rule_id": "broad-exception-handling",
    "severity": "error",
    "message": "Bare 'except:' clause used during flag assignment.",
    "line": 75,
    "suggestion": "Specify the exception type being handled."
  },
  {
    "rule_id": "inconsistent-return-types",
    "severity": "info",
    "message": "The function returns a tuple (DataFrame, dict), which is acceptable, but the logic inside the function is highly unpredictable.",
    "line": 91,
    "suggestion": "Ensure the return structure is documented via type hints."
  }
]
```