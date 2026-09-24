### Code Review

**Naming Conventions**
* **Inconsistent Casing:** The codebase mixes `camelCase` (`playerX`, `enemyList`, `scoreValue`, `runningGame`, `initGame`) with `snake_case` (standard for Python) and `UPPER_CASE` for constants. Suggest using `snake_case` for all variables and functions (e.g., `player_x`, `init_game`) to follow PEP 8.

**Software Engineering Standards & RAG Rules**
* **Heavy Use of Globals:** The code relies extensively on `global` keywords and module-level mutable state (`playerX`, `enemyList`, etc.). This creates tight coupling and makes the code difficult to test or extend. Suggest encapsulating the game state into a `Game` class or a state dictionary.
* **Lack of Modularity:** The `drawEverything` function handles both rendering logic and UI text creation. Consider separating the rendering of game objects from the UI overlay.

**Logic & Correctness**
* **Hard-coded Colors:** RGB tuples like `(0, 255, 0)` and `(255, 0, 0)` are used directly in the drawing logic. These should be defined as named constants (e.g., `COLOR_PLAYER = (0, 255, 0)`) to improve maintainability.

**Performance & Security**
* **Font Initialization:** `pygame.font.SysFont(None, 36)` is called inside `drawEverything`, meaning a new font object is created every single frame (27 times per second). This is a performance bottleneck; move the font initialization to `initGame`.

**Readability & Consistency**
* **Formatting:** Some `if` statements are written on a single line (e.g., `if playerX < 0: playerX = 0`). For better readability and consistency, these should be expanded to two lines.