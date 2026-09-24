### Code Review

**Naming Conventions**
* **Variable Naming:** Use `snake_case` for variables and functions to adhere to PEP 8 (e.g., `playerX` $\rightarrow$ `player_x`, `enemyList` $\rightarrow$ `enemy_list`, `initGame` $\rightarrow$ `init_game`).

**Software Engineering Standards**
* **Shared Mutable State:** The code relies heavily on `global` variables (`playerX`, `scoreValue`, etc.). This creates tight coupling and makes the code difficult to test or extend. 
    * *Suggestion:* Encapsulate the game state into a class (e.g., `Game`) or a data structure passed as an argument to functions.
* **Modularity:** The `drawEverything` function handles both the logic of creating a font object and the rendering. 
    * *Suggestion:* Initialize the font once in `initGame` rather than recreating it every frame to improve performance.

**Logic & Correctness**
* **Collision Logic:** The `checkCollision` function increments the score and resets the enemy position upon collision. While logically functional, it lacks a "game over" condition or a way to lose, which is atypical for this type of game loop.

**Performance & Security**
* **Resource Management:** The `pygame.font.SysFont` call inside the main loop is a performance bottleneck as it accesses system resources every frame. Move this to the initialization phase.

**Readability & Consistency**
* **Formatting:** Some `if` statements are written on a single line (e.g., `if playerX < 0: playerX = 0`). For better readability, move the action to a new indented line.