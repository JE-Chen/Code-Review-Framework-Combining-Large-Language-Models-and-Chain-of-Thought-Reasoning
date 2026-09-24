[
  {
    "rule_id": "no-global-state",
    "severity": "warning",
    "message": "Excessive use of global variables makes the code harder to test and maintain.",
    "line": 5,
    "suggestion": "Encapsulate game state in a class or module to avoid global variables."
  },
  {
    "rule_id": "bad-variable-names",
    "severity": "warning",
    "message": "Variable names 'vx' and 'vy' are too short and not descriptive.",
    "line": 8,
    "suggestion": "Use descriptive names like 'player_velocity_x' and 'player_velocity_y'."
  },
  {
    "rule_id": "magic-number",
    "severity": "warning",
    "message": "Magic number 7 is used without explanation.",
    "line": 25,
    "suggestion": "Define a constant (e.g., NUM_ENEMIES = 7) for the enemy count."
  },
  {
    "rule_id": "missing-docstrings",
    "severity": "info",
    "message": "Functions lack docstrings to explain purpose and behavior.",
    "line": 20,
    "suggestion": "Add docstrings to all public functions describing parameters and effects."
  },
  {
    "rule_id": "missing-structure-doc",
    "severity": "info",
    "message": "EnemyList structure (position as [x, y]) is not documented.",
    "line": 10,
    "suggestion": "Document enemyList element structure or use a namedtuple for clarity."
  }
]