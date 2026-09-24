```json
[
  {
    "rule_id": "shared-mutable-state",
    "severity": "error",
    "message": "The use of a global dictionary 'STATE' to manage game state introduces hidden coupling and makes the code difficult to test and reason about.",
    "line": 15,
    "suggestion": "Encapsulate the game state within a class (e.g., GameState) and pass an instance of that class to the functions."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "The function name 'do_everything' is not descriptive and lacks semantic clarity regarding its actual purpose.",
    "line": 24,
    "suggestion": "Rename to something more descriptive, such as 'update_game_state' or 'handle_game_logic'."
  },
  {
    "rule_id": "performance-bottleneck",
    "severity": "info",
    "message": "The font object is created every frame inside the draw loop, which is an expensive operation.",
    "line": 58,
    "suggestion": "Initialize the font object once outside the main loop and reuse it."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "warning",
    "message": "The expression 'int(math.sqrt(STATE[\"velocity\"] ** 2))' is a computationally expensive way to calculate the absolute value of velocity.",
    "line": 42,
    "suggestion": "Use 'abs(STATE[\"velocity\"])' for better performance and readability."
  },
  {
    "rule_id": "magic-number",
    "severity": "info",
    "message": "The value '57' in clock.tick() is a magic number.",
    "line": 76,
    "suggestion": "Define a named constant such as 'FPS = 57' at the top of the file."
  }
]
```