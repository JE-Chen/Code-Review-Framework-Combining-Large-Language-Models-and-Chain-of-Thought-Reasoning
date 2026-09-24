```json
[
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '40' used in filter_high_scores(). Consider extracting to a named constant.",
    "line": 15,
    "suggestion": "Extract '40' into a named constant like MIN_HIGH_SCORE."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '50' used in process_misc(). Consider extracting to a named constant.",
    "line": 27,
    "suggestion": "Extract '50' into a named constant like DEFAULT_THRESHOLD."
  },
  {
    "rule_id": "no-duplicate-code",
    "severity": "warning",
    "message": "Duplicate access pattern for DATA['users'] in calculate_average_scores() and filter_high_scores(). Consider abstracting.",
    "line": 5,
    "suggestion": "Refactor repeated data access into a helper function."
  },
  {
    "rule_id": "no-duplicate-code",
    "severity": "warning",
    "message": "Duplicate conditional checks on flags in main(). Consider refactoring nested conditionals.",
    "line": 36,
    "suggestion": "Simplify nested if statements using early returns or logical grouping."
  },
  {
    "rule_id": "no-hardcoded-strings",
    "severity": "warning",
    "message": "Hardcoded string 'X' used in main(). Consider defining as a constant or enum.",
    "line": 34,
    "suggestion": "Define 'X' as a constant or use an enum for better maintainability."
  },
  {
    "rule_id": "no-global-state",
    "severity": "warning",
    "message": "Direct access to global variable DATA. This reduces testability and modularity.",
    "line": 5,
    "suggestion": "Pass DATA as a parameter to functions instead of accessing globally."
  },
  {
    "rule_id": "no-implicit-returns",
    "severity": "info",
    "message": "Functions do not explicitly return None when no value is returned.",
    "line": 12,
    "suggestion": "Consider adding explicit return statements for clarity."
  },
  {
    "rule_id": "no-unreachable-code",
    "severity": "warning",
    "message": "Unreachable code after else clause in nested conditionals within main().",
    "line": 41,
    "suggestion": "Verify that all branches are logically reachable and simplify structure."
  }
]
```