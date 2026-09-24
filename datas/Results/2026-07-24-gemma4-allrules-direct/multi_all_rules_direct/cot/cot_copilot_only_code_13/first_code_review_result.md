### Code Review

**1. Readability & Consistency**
* **Formatting:** The code generally follows a consistent style, but some conditional statements are written on a single line (e.g., `if playerX < 0: playerX = 0`), which reduces readability. Prefer standard multi-line blocks.

**2. Naming Conventions**
* **Variable Naming:** Use `snake_case` for variables and functions to adhere to PEP 8 standards (e.g., `playerX` $\rightarrow$ `player_x`, `enemyList` $\rightarrow$ `enemy_list`, `initGame` $\rightarrow$ `init_game`).
* **Descriptiveness:** `vx` and `vy` are acceptable for velocity, but `scoreValue` is redundant; `score` is sufficient.

**3. Software Engineering Standards**
* **Shared Mutable State:** The code relies heavily on `global` variables (e.g., `playerX`, `enemyList`, `scoreValue`). This creates tight coupling and makes the code difficult to test or extend.
    * *Suggestion:* Encapsulate the game state into a class or a data structure and pass it as an argument to functions.
* **Modularity:** The `drawEverything` function handles both the logic of creating a font object and the rendering.
    * *Suggestion:* Initialize the font once in `initGame` rather than recreating it every frame (30 times per second).

**4. Logic & Correctness**
* **Collision Logic:** The collision detection is correct for AABB (Axis-Aligned Bounding Boxes).
* **Boundary Handling:** Player movement is correctly clamped to the screen dimensions.

**5. Performance & Security**
* **Resource Management:** Creating a new `pygame.font.SysFont` object inside the main loop (`drawEverything`) is a performance bottleneck. Move this to the initialization phase.

**6. Documentation & Testing**
* **Documentation:** The code lacks docstrings or comments explaining the purpose of the functions.
* **Testing:** There are no unit tests for the collision or movement logic.

### Summary of Improvement Suggestions
* **Refactor Globals:** Move game state into a `GameState` class or a dictionary to remove `global` keywords.
* **Optimize Rendering:** Move `font = pygame.font.SysFont(None, 36)` out of the loop and into `initGame`.
* **Standardize Naming:** Rename functions and variables to `snake_case`.
* **Clean Up Conditionals:** Expand single-line `if` statements to multiple lines for better clarity.