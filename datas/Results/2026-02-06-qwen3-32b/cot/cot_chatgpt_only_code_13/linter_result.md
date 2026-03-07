[
  {
    "rule_id": "magic-number",
    "severity": "warning",
    "message": "Magic number 17 used as enemy spawn interval. Replace with descriptive constant.",
    "line": 20,
    "suggestion": "Define ENEMY_SPAWN_INTERVAL = 17"
  },
  {
    "rule_id": "poorly-named-function",
    "severity": "warning",
    "message": "Function name 'do_the_whole_game_because_why_not' is non-descriptive and unprofessional.",
    "line": 25,
    "suggestion": "Rename to 'game_loop' or 'main_game_loop'"
  },
  {
    "rule_id": "poorly-named-variable",
    "severity": "warning",
    "message": "Variable name 'STRANGE_FLAGS' is non-descriptive and confusing.",
    "line": 19,
    "suggestion": "Rename to 'player_panic' or 'panic_state'"
  },
  {
    "rule_id": "broad-exception-catch",
    "severity": "error",
    "message": "Broad exception catch (except: pass) hides potential bugs and security issues.",
    "line": 89,
    "suggestion": "Catch specific exceptions or log errors instead of ignoring all exceptions"
  },
  {
    "rule_id": "magic-number",
    "severity": "warning",
    "message": "Magic number 300 used for panic reset interval. Replace with descriptive constant.",
    "line": 132,
    "suggestion": "Define PANIC_RESET_INTERVAL = 300"
  }
]