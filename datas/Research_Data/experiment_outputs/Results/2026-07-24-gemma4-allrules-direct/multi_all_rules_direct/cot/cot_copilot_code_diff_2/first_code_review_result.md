### Code Review

**Naming Conventions**
* **Inconsistent Naming Style:** The code mixes `camelCase` (`playerX`, `enemyList`, `scoreValue`, `initGame`) with `SNAKE_CASE` (`WIDTH`, `PLAYER_SIZE`). Per Python standards (PEP 8), functions and variables should use `snake_case`.
* **Vague Variable Names:** `vx` and `vy` should be renamed to `velocity_x` and `velocity_y` for better clarity.

**Software Engineering Standards**
* **Excessive Use of Global State:** The code relies heavily on `global` variables (`playerX`, `playerY`, `enemyList`, etc.). This creates hidden coupling and makes the code difficult to test or extend. Consider encapsulating the game state in a class or a data structure.
* **Lack of Modularity:** The `drawEverything` function handles both the clearing of the screen, drawing entities, and rendering the UI. These should be split into smaller, focused functions.

**Logic & Correctness**
* **Hard-coded Magic Numbers:** The color tuples (e.g., `(0, 255, 0)`) and the clock tick rate (`27`) are magic numbers. These should be defined as named constants at the top of the file.

**RAG Rule Violations**
* **Shared Mutable State:** The `enemyList` is a global mutable list modified across multiple functions (`initGame`, `checkCollision`), which increases the risk of side effects.
* **Implicit Truthiness:** While not a bug here, the logic relies on implicit truthiness for `runningGame`. Explicit comparisons are preferred for clarity.

**Suggestions for Improvement**
* **Refactor to a Class:** Wrap the game logic in a `Game` class to eliminate `global` keywords and group related state and behavior.
* **Standardize Naming:** Rename all functions and variables to `snake_case` to align with Python conventions.
* **Extract Constants:** Move colors and frame rates to named constants (e.g., `COLOR_PLAYER = (0, 255, 0)`).