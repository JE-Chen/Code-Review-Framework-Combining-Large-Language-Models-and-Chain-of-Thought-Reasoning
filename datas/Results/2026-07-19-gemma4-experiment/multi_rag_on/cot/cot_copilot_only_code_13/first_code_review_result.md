### Code Review

**1. Readability & Consistency**
* **Formatting:** The code is generally clean, but some conditional statements are written on a single line (e.g., `if playerX < 0: playerX = 0`), which deviates from PEP 8 standards.

**2. Naming Conventions**
* **Case Consistency:** The codebase mixes `camelCase` (`playerX`, `enemyList`, `scoreValue`, `runningGame`) with `snake_case` (standard for Python) and `UPPER_CASE` for constants. Recommend using `snake_case` for all variables and functions to align with Python conventions.

**3. Software Engineering Standards**
* **Global State:** The code relies heavily on `global` variables (e.g., `global playerX, playerY, vx, vy`). This makes the code harder to test and maintain. Suggest encapsulating the game state into a class (e.g., `Game` or `GameState`).
* **Data Structures:** `enemyList` stores enemies as lists of coordinates. Using a `pygame.Rect` object or a named tuple would improve readability and provide built-in collision methods.

**4. Logic & Correctness**
* **Collision Logic:** The collision detection is manually implemented. Since `pygame` is being used, `pygame.Rect.colliderect()` would be more efficient and less prone to manual calculation errors.

**5. Performance & Security**
* **Resource Management:** The `pygame.font.SysFont` is called inside `drawEverything()`, meaning a new font object is created every single frame (30 times per second). This is a performance bottleneck; the font should be initialized once in `initGame()`.

**6. Documentation & Testing**
* **Missing Documentation:** There are no docstrings or comments explaining the purpose of the functions.
* **Testing:** No unit tests are provided for the collision or movement logic.