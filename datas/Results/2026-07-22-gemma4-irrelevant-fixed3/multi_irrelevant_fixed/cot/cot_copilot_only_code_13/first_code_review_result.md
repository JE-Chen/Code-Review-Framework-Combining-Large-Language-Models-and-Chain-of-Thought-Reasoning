### Code Review

**Naming Conventions**
* **Variable Naming:** Use `snake_case` for variables and functions to follow PEP 8 standards (e.g., `playerX` $\rightarrow$ `player_x`, `enemyList` $\rightarrow$ `enemy_list`, `scoreValue` $\rightarrow$ `score`).
* **Descriptive Naming:** `vx` and `vy` are acceptable for velocity, but `player_velocity_x` would be more explicit.

**Software Engineering Standards**
* **Global State:** The code relies heavily on `global` variables. This makes the code harder to maintain and test. Consider wrapping the game state in a `Game` class or passing a state object between functions.
* **Data Structures:** `enemyList` stores enemies as lists of coordinates. Using a `pygame.Rect` object for enemies and the player would simplify collision detection and movement logic.
* **Modularity:** The `drawEverything` function handles both rendering and font initialization. Move `pygame.font.SysFont` outside the main loop to avoid recreating the font object every frame.

**Logic & Correctness**
* **Collision Logic:** The collision detection is correct, but using `pygame.Rect.colliderect()` would be more idiomatic and readable.

**Readability & Consistency**
* **Formatting:** Some `if` statements are written on a single line (e.g., `if playerX < 0: playerX = 0`). For consistency and readability, move the action to a new indented line.

**Performance**
* **Resource Management:** As mentioned, initializing the font inside `drawEverything` (which runs 30 times per second) is inefficient. Initialize it once in `initGame`.