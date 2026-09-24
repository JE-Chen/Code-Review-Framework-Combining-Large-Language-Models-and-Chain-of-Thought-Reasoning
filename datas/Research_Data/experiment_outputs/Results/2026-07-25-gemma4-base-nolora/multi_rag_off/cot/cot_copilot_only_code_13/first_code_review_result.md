### Code Review

**1. Readability & Consistency**
* **Formatting:** The code generally follows a consistent style, though some one-line `if` statements (e.g., `if playerX < 0: playerX = 0`) should be expanded to multiple lines to adhere to PEP 8 standards.

**2. Naming Conventions**
* **Case Consistency:** The codebase mixes `camelCase` (`enemyList`, `scoreValue`, `runningGame`) with `snake_case` (standard for Python) and `UPPER_CASE` for constants. Recommend converting all variables and functions to `snake_case` (e.g., `enemy_list`, `score_value`).

**3. Software Engineering Standards**
* **Global State:** The code relies heavily on `global` variables (e.g., `global playerX, playerY`). This makes the code harder to test and maintain. 
    * *Suggestion:* Encapsulate the game state into a `Game` class or pass state objects as arguments to functions.
* **Data Structures:** `enemyList` stores enemies as lists of coordinates `[x, y]`. 
    * *Suggestion:* Use `pygame.Rect` objects for enemies. This would replace the manual collision logic in `checkCollision` with the built-in `colliderect()` method.

**4. Logic & Correctness**
* **Collision Logic:** The collision detection is correct for AABB (Axis-Aligned Bounding Boxes).
* **Boundary Handling:** Player movement is correctly clamped to the screen dimensions.

**5. Performance & Security**
* **Resource Management:** `pygame.font.SysFont` is called inside `drawEverything()`, meaning a new font object is created every single frame (30 times per second).
    * *Suggestion:* Initialize the font once in `initGame()` and reuse the object to avoid unnecessary memory allocation and CPU overhead.

**6. Documentation & Testing**
* **Documentation:** The code lacks docstrings for functions and a high-level description of the game logic.
* **Testing:** No unit tests are present for the movement or collision logic.