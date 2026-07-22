### Code Review

**Naming Conventions**
* **Inconsistent Casing:** The code mixes `camelCase` (`playerX`, `enemyList`, `scoreValue`, `initGame`) with `snake_case` (standard for Python) and `UPPER_CASE` for constants. Suggest using `snake_case` for all variables and functions (e.g., `player_x`, `init_game`) to follow PEP 8.

**Software Engineering Standards**
* **Excessive Use of Global State:** Almost every function relies on `global` keywords to modify state. This makes the code difficult to test and maintain. Suggest encapsulating the game state into a `Game` class or passing state as arguments.
* **Lack of Modularity:** The `drawEverything` function handles both rendering and font initialization. Creating the `font` object every frame is inefficient.

**Logic & Correctness**
* **Hardcoded Frame Rate:** `clock.tick(27)` is an unusual value. Standard values are typically 30 or 60 for smoother movement.

**Readability & Consistency**
* **Inline Conditionals:** Lines like `if playerX < 0: playerX = 0` are less readable. Suggest moving the assignment to a new line.
* **Magic Numbers:** The color tuples (e.g., `(0, 255, 0)`) should be defined as constants (e.g., `COLOR_PLAYER = (0, 255, 0)`) for clarity.

**Performance & Security**
* **Resource Allocation:** `pygame.font.SysFont(None, 36)` is called inside the main loop (via `drawEverything`). This creates a new font object every frame, which will cause performance degradation over time. Move this to `initGame`.