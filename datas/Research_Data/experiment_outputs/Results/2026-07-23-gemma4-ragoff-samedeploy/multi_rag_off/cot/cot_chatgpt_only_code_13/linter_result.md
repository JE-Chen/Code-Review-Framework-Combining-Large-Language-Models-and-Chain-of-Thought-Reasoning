```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 'CLOCK_THING' uses non-standard naming. Constants should be descriptive, and this name is vague.",
    "line": 15,
    "suggestion": "Rename to 'clock' or 'GAME_CLOCK'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Variable 'MAGIC' is a 'magic number' with a non-descriptive name.",
    "line": 21,
    "suggestion": "Rename to 'ENEMY_SPAWN_INTERVAL' or similar."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'do_the_whole_game_because_why_not' is unprofessional and not descriptive of its purpose.",
    "line": 27,
    "suggestion": "Rename to 'main_game_loop' or 'run_game'."
  },
  {
    "rule_id": "software-engineering-standards",
    "severity": "error",
    "message": "The game loop is contained within a single monolithic function, making it difficult to test and maintain.",
    "line": 27,
    "suggestion": "Refactor logic into separate functions (e.g., 'handle_input', 'update_physics', 'render')."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "warning",
    "message": "The player's position is clamped to W and H, but the player's width/height (20px) is not accounted for, allowing the player to partially move off-screen.",
    "line": 51,
    "suggestion": "Clamp x to 'W - 20' and y to 'H - 20'."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "error",
    "message": "Bare 'except: pass' block suppresses all exceptions, including KeyboardInterrupt and SystemExit, making debugging nearly impossible.",
    "line": 85,
    "suggestion": "Remove the try-except block and handle specific errors, or use a proper collision detection loop that doesn't risk index errors."
  },
  {
    "rule_id": "performance-security",
    "severity": "info",
    "message": "Using 'BULLETS.remove(b)' inside a nested loop while iterating over a slice 'BULLETS[:]' is inefficient for large lists.",
    "line": 82,
    "suggestion": "Consider using a list comprehension to filter out inactive bullets at the end of the frame."
  }
]
```