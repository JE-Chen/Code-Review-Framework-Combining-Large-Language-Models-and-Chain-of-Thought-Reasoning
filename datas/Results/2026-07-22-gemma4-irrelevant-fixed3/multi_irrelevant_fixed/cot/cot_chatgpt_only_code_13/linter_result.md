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
    "message": "Variable 'MAGIC' is a 'magic number' constant with a non-descriptive name.",
    "line": 21,
    "suggestion": "Rename to 'ENEMY_SPAWN_INTERVAL' or similar."
  },
  {
    "rule_id": "naming-convention",
    "severity": "error",
    "message": "Function name 'do_the_whole_game_because_why_not' is unprofessional and not descriptive of its purpose.",
    "line": 27,
    "suggestion": "Rename to 'main_game_loop' or 'run_game'."
  },
  {
    "rule_id": "software-engineering-standards",
    "severity": "warning",
    "message": "The game loop is contained within a single monolithic function, reducing maintainability and testability.",
    "line": 27,
    "suggestion": "Refactor logic into separate functions for input handling, updating state, and rendering."
  },
  {
    "rule_id": "logic-correctness",
    "severity": "warning",
    "message": "Bare 'except: pass' block suppresses all exceptions, making debugging difficult and potentially hiding critical errors.",
    "line": 91,
    "suggestion": "Catch specific exceptions (e.g., ValueError) or remove the try-except block and handle list modification safely."
  },
  {
    "rule_id": "performance-security",
    "severity": "info",
    "message": "Using 'BULLETS.remove(b)' inside a nested loop while iterating over a slice is inefficient for large lists.",
    "line": 88,
    "suggestion": "Consider using a list comprehension or a flag to mark objects for removal at the end of the frame."
  }
]
```