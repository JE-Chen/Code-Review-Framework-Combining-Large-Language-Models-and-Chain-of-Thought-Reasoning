```json
[
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '40' used in filter_high_scores(). Consider replacing with a named constant for clarity.",
    "line": 15,
    "suggestion": "Define a constant like HIGH_SCORE_THRESHOLD = 40 and use it instead."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '50' used in process_misc(). Consider replacing with a named constant for clarity.",
    "line": 26,
    "suggestion": "Define a constant like THRESHOLD = 50 and use it instead."
  },
  {
    "rule_id": "no-duplicate-code",
    "severity": "warning",
    "message": "Duplicate access pattern for DATA['users'] in calculate_average_scores() and filter_high_scores(). Consider extracting common logic into a helper function.",
    "line": 7,
    "suggestion": "Refactor repeated access to DATA['users'] into a shared variable or helper function."
  },
  {
    "rule_id": "no-duplicate-code",
    "severity": "warning",
    "message": "Duplicate access pattern for DATA['config']['threshold'] in process_misc(). Consider extracting common logic into a helper function.",
    "line": 24,
    "suggestion": "Refactor repeated access to DATA['config']['threshold'] into a shared variable or helper function."
  },
  {
    "rule_id": "no-hardcoded-strings",
    "severity": "warning",
    "message": "Hardcoded string 'X' in main(). Consider using a constant or enum for better maintainability.",
    "line": 33,
    "suggestion": "Use a constant like MODE_X = 'X' and reference it throughout the code."
  },
  {
    "rule_id": "no-unreachable-code",
    "severity": "warning",
    "message": "Unreachable code after else clause in main(). The final else block will never execute due to early return.",
    "line": 42,
    "suggestion": "Remove redundant conditional structure or restructure logic to ensure all paths are reachable."
  },
  {
    "rule_id": "no-implicit-boolean-conversion",
    "severity": "warning",
    "message": "Implicit boolean conversion in conditionals may lead to unexpected behavior; consider explicit comparisons.",
    "line": 36,
    "suggestion": "Use explicit boolean checks like 'if DATA['config']['flags'][0] is True:' for clarity."
  },
  {
    "rule_id": "no-global-state",
    "severity": "warning",
    "message": "Direct usage of global variable DATA within functions makes testing difficult and reduces modularity.",
    "line": 4,
    "suggestion": "Pass DATA as a parameter to functions to improve testability and reduce coupling."
  }
]
```