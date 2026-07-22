```json
[
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number 57 used in clock.tick(). Consider defining it as a named constant for clarity.",
    "line": 45,
    "suggestion": "Define FPS as a constant like `FPS = 57` and use it in `clock.tick(FPS)`."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number 255 used in screen.fill() and color calculations. Should be replaced with a named constant.",
    "line": 33,
    "suggestion": "Use a constant like `MAX_COLOR_VALUE = 255` instead of hardcoding 255."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic numbers 10 and 15 used in circle radius and score-based adjustments. These should be constants.",
    "line": 39,
    "suggestion": "Define constants such as `PLAYER_RADIUS = 10` and `RADIUS_MODIFIER = 15`."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number 24 used in font size. Should be replaced with a named constant.",
    "line": 41,
    "suggestion": "Use a constant like `FONT_SIZE = 24`."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number 7 used in modulo operation. It's unclear what this represents; consider naming it.",
    "line": 23,
    "suggestion": "Rename `7` to something meaningful like `SCORE_INCREMENT_BASE`."
  },
  {
    "rule_id": "no-global-state",
    "severity": "error",
    "message": "Global state is used extensively via the STATE dictionary. This makes testing and modularity difficult.",
    "line": 15,
    "suggestion": "Refactor to encapsulate game state into a class or pass state explicitly to functions."
  },
  {
    "rule_id": "no-duplicate-code",
    "severity": "warning",
    "message": "The loop that updates player position in move_player() has repeated logic for movement direction.",
    "line": 28,
    "suggestion": "Consider extracting direction-specific logic into helper functions to reduce duplication."
  },
  {
    "rule_id": "no-unnecessary-math",
    "severity": "warning",
    "message": "Using math.sqrt on velocity squared just to get absolute value. This is redundant and inefficient.",
    "line": 29,
    "suggestion": "Replace `int(math.sqrt(STATE['velocity'] ** 2))` with `abs(STATE['velocity'])`."
  },
  {
    "rule_id": "no-unsafe-operations",
    "severity": "warning",
    "message": "Player movement uses modulo operations without checking for zero velocity, which could lead to unexpected behavior.",
    "line": 31,
    "suggestion": "Add a check to ensure velocity is non-zero before performing modulo operations."
  },
  {
    "rule_id": "no-unexpected-side-effects",
    "severity": "warning",
    "message": "do_everything() modifies global STATE directly. Side effects make code harder to reason about.",
    "line": 19,
    "suggestion": "Avoid modifying shared mutable state inside functions. Pass state as parameters or return updated values."
  },
  {
    "rule_id": "no-inconsistent-naming",
    "severity": "warning",
    "message": "Function name 'do_everything' does not clearly describe its purpose. It's too generic.",
    "line": 19,
    "suggestion": "Rename function to something more descriptive like 'update_game_state' or 'process_input_and_update'."
  },
  {
    "rule_id": "no-hardcoded-strings",
    "severity": "warning",
    "message": "Hardcoded string 'Score-ish: ' is used directly in render. Should be extracted to a constant.",
    "line": 42,
    "suggestion": "Define a constant like `SCORE_LABEL = 'Score-ish: '` to improve maintainability."
  },
  {
    "rule_id": "no-unreachable-code",
    "severity": "warning",
    "message": "In move_player(), using `STATE['velocity'] or 1` can cause unintended behavior if velocity is 0.",
    "line": 32,
    "suggestion": "Replace `or 1` with explicit conditional checks to avoid confusion."
  }
]
```