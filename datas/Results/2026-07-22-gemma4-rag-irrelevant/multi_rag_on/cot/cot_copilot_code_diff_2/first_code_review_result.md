### Code Review

**Naming Conventions**
* **Inconsistent Casing:** The code mixes `camelCase` (`playerX`, `enemyList`, `scoreValue`, `runningGame`) with `snake_case` (standard for Python) and `UPPER_CASE` for constants. Suggest using `snake_case` for all variables and functions (e.g., `player_x`, `enemy_list`, `init_game`) to follow PEP 8.
* **Vague Variable Names:** In `drawEverything`, the variable `e` is used for enemies. Use `enemy` for better clarity.

**Software Engineering Standards**
* **Excessive Use of Globals:** Almost every function relies on `global` keywords to modify state. This makes the code hard to test and maintain. Suggest encapsulating the game state into a class (e.g., `Game`) or passing state as arguments.
* **Lack of Modularity:** The `drawEverything` function handles both clearing the screen, drawing entities, and rendering text. These should be split into smaller, specialized functions.

**Logic & Correctness**
* **Hardcoded Frame Rate:** `clock.tick(27)` uses an unusual value. Standard values are typically 30 or 60 for smoother movement.
* **Collision Logic:** The collision detection is correct for AABB (Axis-Aligned Bounding Boxes), but the logic simply teleports the enemy and increments the score without any visual or audio feedback.

**Readability & Consistency**
* **Formatting:** Multiple statements on one line (e.g., `if playerX < 0: playerX = 0`) reduce readability. Move the action to a new indented line.
* **Magic Numbers:** Colors (e.g., `(0, 255, 0)`) are hardcoded in the draw loop. Define these as constants at the top (e.g., `COLOR_PLAYER = (0, 255, 0)`).

**Performance & Security**
* **Font Initialization:** `pygame.font.SysFont(None, 36)` is called every single frame inside `drawEverything`. This is a significant performance bottleneck. Initialize the font once in `initGame` and reuse the object.