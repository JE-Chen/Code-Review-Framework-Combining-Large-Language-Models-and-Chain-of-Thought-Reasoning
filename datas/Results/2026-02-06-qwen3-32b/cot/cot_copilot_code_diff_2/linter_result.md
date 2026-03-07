[
  {
    "rule_id": "no-global-state",
    "severity": "error",
    "message": "Extensive use of global variables for game state (playerX, playerY, vx, vy, enemyList, scoreValue, runningGame). This violates modularity and testability principles.",
    "line": 6,
    "suggestion": "Encapsulate game state in a class instead of using global variables."
  },
  {
    "rule_id": "naming-inconsistent",
    "severity": "warning",
    "message": "Variable `enemyList` uses camelCase while other constants (WIDTH, HEIGHT) use ALL_CAPS. Inconsistent naming style.",
    "line": 10,
    "suggestion": "Rename to `enemies` (snake_case) to match naming conventions."
  },
  {
    "rule_id": "naming-simpler",
    "severity": "warning",
    "message": "Variable `scoreValue` is redundant; `score` is sufficient and more conventional.",
    "line": 11,
    "suggestion": "Rename to `score` for simplicity."
  },
  {
    "rule_id": "naming-boolean",
    "severity": "warning",
    "message": "Boolean variable `runningGame` should be named `running` for clarity as a flag.",
    "line": 12,
    "suggestion": "Rename to `running`."
  },
  {
    "rule_id": "no-docstrings",
    "severity": "info",
    "message": "Functions lack docstrings explaining purpose, parameters, and return values.",
    "line": 15,
    "suggestion": "Add docstrings to all functions for better maintainability."
  },
  {
    "rule_id": "no-tests",
    "severity": "info",
    "message": "No unit tests provided for game logic (collision handling, movement, rendering).",
    "line": 50,
    "suggestion": "Implement unit tests for collision detection and game state transitions."
  }
]