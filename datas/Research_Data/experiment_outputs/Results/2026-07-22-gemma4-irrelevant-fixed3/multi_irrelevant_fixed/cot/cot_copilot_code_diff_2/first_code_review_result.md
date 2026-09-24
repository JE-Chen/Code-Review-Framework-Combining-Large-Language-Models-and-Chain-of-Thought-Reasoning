### Code Review

**Naming Conventions**
* **Inconsistent Casing:** The code mixes `camelCase` (`playerX`, `enemyList`, `scoreValue`, `runningGame`) with `snake_case` (standard for Python) and `UPPER_CASE` for constants. Suggest using `snake_case` for all variables and functions (e.g., `player_x`, `enemy_list`, `init_game`) to follow PEP 8.

**Software Engineering Standards**
* **Excessive Use of Globals:** Almost every function relies on the `global` keyword to modify state. This makes the code harder to test and maintain. Suggest encapsulating the game state into a class or passing parameters to functions.
* **Lack of Modularity:** The `drawEverything` function handles both the logic of creating a font object and the rendering. The font should be initialized once in `initGame` rather than every frame.

**Logic & Correctness**
* **Hardcoded Frame Rate:** `clock.tick(27)` uses an unusual value. While not a bug, standard values (30 or 60) are typically preferred for smoother movement.

**Readability & Consistency**
* **Inline Conditionals:** The boundary checks in `movePlayer` (e.g., `if playerX < 0: playerX = 0`) are written on a single line. For better readability, these should be expanded to multiple lines.

**Suggestions for Improvement**
* **State Management:** Wrap the game logic in a `Game` class to eliminate `global` variables.
* **Resource Optimization:** Move `pygame.font.SysFont` out of the main loop to prevent repeated object creation every frame.