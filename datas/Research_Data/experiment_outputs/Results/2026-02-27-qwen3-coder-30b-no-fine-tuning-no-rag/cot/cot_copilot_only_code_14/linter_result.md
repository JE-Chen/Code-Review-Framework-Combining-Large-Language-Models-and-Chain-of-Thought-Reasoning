```json
[
  {
    "rule_id": "no-global-variables",
    "severity": "warning",
    "message": "Usage of global variables (dataFrameLike, resultCache, textOutput, tableWidget, labelStatus) reduces modularity and testability.",
    "line": 6,
    "suggestion": "Refactor to use local variables or pass dependencies as parameters."
  },
  {
    "rule_id": "no-duplicate-code",
    "severity": "warning",
    "message": "Duplicate computation of `statistics.median(vals)` in `analyzeData()` function.",
    "line": 24,
    "suggestion": "Store the median value in a variable to avoid recomputation."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic numbers used in conditional checks (e.g., 5, 10, 50).",
    "line": 15,
    "suggestion": "Replace magic numbers with named constants for better readability."
  },
  {
    "rule_id": "no-unneeded-ternary",
    "severity": "warning",
    "message": "Unnecessary ternary operator usage when simple assignment would suffice.",
    "line": 21,
    "suggestion": "Simplify conditional assignment by directly assigning 'HIGH' or 'LOW'."
  },
  {
    "rule_id": "no-side-effects-in-functions",
    "severity": "warning",
    "message": "Functions like `generateData`, `showData` modify global state without explicit parameterization.",
    "line": 10,
    "suggestion": "Avoid modifying global state within functions; consider returning values instead."
  },
  {
    "rule_id": "no-empty-blocks",
    "severity": "info",
    "message": "The `else` block in `analyzeData` handles an edge case but could benefit from more descriptive error handling.",
    "line": 25,
    "suggestion": "Add logging or additional context for why no data exists."
  }
]
```