```json
[
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'do_everything' is not descriptive and violates semantic clarity.",
    "line": 23,
    "suggestion": "Rename to something more specific, such as 'update_game_state'."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'draw_stuff' is not descriptive and violates semantic clarity.",
    "line": 48,
    "suggestion": "Rename to 'render_frame' or 'draw_game_objects'."
  },
  {
    "rule_id": "software-engineering-standards",
    "severity": "info",
    "message": "The use of a global dictionary 'STATE' for game state management hinders testability and modularity.",
    "line": 15,
    "suggestion": "Encapsulate game state within a class or pass it as an argument to functions."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "warning",
    "message": "The expression 'STATE[\"velocity\"] or 1' creates inconsistent movement behavior when velocity is 0.",
    "line": 44,
    "suggestion": "Use a consistent movement logic that handles zero velocity explicitly."
  },
  {
    "rule_id": "performance-bottleneck",
    "severity": "warning",
    "message": "Creating a new font object 'pygame.font.SysFont(None, 24)' every frame inside the draw loop is inefficient.",
    "line": 58,
    "suggestion": "Initialize the font object once outside the main loop and reuse it."
  }
]
```