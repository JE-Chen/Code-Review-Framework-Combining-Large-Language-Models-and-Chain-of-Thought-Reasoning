```json
[
  {
    "rule_id": "global-variables",
    "severity": "warning",
    "message": "Use of global variables reduces modularity and testability. Consider encapsulating game state in a class.",
    "line": 6,
    "suggestion": "Refactor to use a class-based approach to manage game state."
  },
  {
    "rule_id": "magic-numbers",
    "severity": "warning",
    "message": "Magic numbers like 9 (enemy count) and 27 (FPS) should be replaced with named constants for clarity.",
    "line": 15,
    "suggestion": "Define constants for enemy count and FPS to improve readability."
  },
  {
    "rule_id": "inconsistent-naming",
    "severity": "warning",
    "message": "Variable naming is inconsistent; some use snake_case while others use camelCase. Stick to one convention.",
    "line": 7,
    "suggestion": "Standardize variable names to snake_case throughout the codebase."
  },
  {
    "rule_id": "duplicate-code",
    "severity": "warning",
    "message": "The collision detection logic is duplicated in multiple places. Extract it into a reusable function.",
    "line": 32,
    "suggestion": "Extract collision checking into a separate helper function for reuse."
  },
  {
    "rule_id": "hardcoded-values",
    "severity": "warning",
    "message": "Hardcoded color values (0, 255, 0) and (255, 0, 0) should be defined as constants.",
    "line": 24,
    "suggestion": "Define color constants for better maintainability and consistency."
  },
  {
    "rule_id": "missing-documentation",
    "severity": "info",
    "message": "Missing docstrings for functions. Adding docstrings improves code understandability.",
    "line": 11,
    "suggestion": "Add docstrings to all functions explaining their purpose, parameters, and return values."
  },
  {
    "rule_id": "tight-coupling",
    "severity": "warning",
    "message": "Functions are tightly coupled through global variables, making them hard to test independently.",
    "line": 11,
    "suggestion": "Pass dependencies explicitly instead of relying on global state."
  },
  {
    "rule_id": "improper-game-loop",
    "severity": "warning",
    "message": "The game loop uses fixed tick rate without considering frame rate variability.",
    "line": 36,
    "suggestion": "Consider using delta time for smoother movement and consistent gameplay speed."
  }
]
```