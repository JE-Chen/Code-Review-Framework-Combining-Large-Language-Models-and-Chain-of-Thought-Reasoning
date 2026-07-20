```json
[
  {
    "rule_id": "shared-mutable-state",
    "severity": "error",
    "message": "Heavy use of global variables (screen, playerX, playerY, vx, vy, enemyList, scoreValue, runningGame) creates hidden coupling and makes the code difficult to test and maintain.",
    "line": 5,
    "suggestion": "Encapsulate game state within a class (e.g., GameState) or pass state explicitly as arguments to functions."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable names 'playerX', 'playerY', 'vx', 'vy', 'enemyList', 'scoreValue', and 'runningGame' do not follow PEP 8 snake_case convention.",
    "line": 6,
    "suggestion": "Rename to 'player_x', 'player_y', 'vx', 'vy', 'enemy_list', 'score_value', and 'running_game'."
  },
  {
    "rule_id": "magic-number",
    "severity": "info",
    "message": "The number of enemies (9) is a hard-coded magic number.",
    "line": 26,
    "suggestion": "Define a constant like 'ENEMY_COUNT = 9' at the top of the file."
  },
  {
    "rule_id": "magic-number",
    "severity": "info",
    "message": "The frame rate (27) is a hard-coded magic number.",
    "line": 74,
    "suggestion": "Define a constant like 'FPS = 27' at the top of the file."
  },
  {
    "rule_id": "readability",
    "severity": "info",
    "message": "Multiple statements on a single line reduce readability.",
    "line": 43,
    "suggestion": "Move 'playerX = 0' to a new line following the 'if' statement."
  },
  {
    "rule_id": "readability",
    "severity": "info",
    "message": "Multiple statements on a single line reduce readability.",
    "line": 44,
    "suggestion": "Move 'playerX = WIDTH-PLAYER_SIZE' to a new line following the 'if' statement."
  },
  {
    "rule_id": "readability",
    "severity": "info",
    "message": "Multiple statements on a single line reduce readability.",
    "line": 45,
    "suggestion": "Move 'playerY = 0' to a new line following the 'if' statement."
  },
  {
    "rule_id": "readability",
    "severity": "info",
    "message": "Multiple statements on a single line reduce readability.",
    "line": 46,
    "suggestion": "Move 'playerY = HEIGHT-PLAYER_SIZE' to a new line following the 'if' statement."
  }
]
```