### Code Review

**1. Readability & Consistency**
* **Formatting:** The code generally follows a consistent style, though some `if` statements are written on a single line (e.g., `if playerX < 0: playerX = 0`), which deviates from PEP 8 standards.

**2. Naming Conventions**
* **Case Consistency:** The codebase mixes `camelCase` (`playerX`, `enemyList`, `scoreValue`, `runningGame`) with `snake_case` (`initGame` is actually camelCase, but `mainLoop` is too). Python standard (PEP 8) recommends `snake_case` for variables and functions.
* **Descriptiveness:** `vx` and `vy` are acceptable for velocity, but `e` in the collision loop should be renamed to `enemy` for better clarity.

**3. Software Engineering Standards**
* **Global State:** The code relies heavily on `global` variables (`global playerX`, `global screen`, etc.). This makes the code difficult to test and maintain. 
    * *Suggestion:* Encapsulate the game state into a class (e.g., `Game`) or pass state as arguments to functions.
* **Modularity:** The `drawEverything` function handles both rendering and font initialization. 
    * *Suggestion:* Initialize the font once in `initGame` rather than creating a new font object every frame (30 times per second).

**4. Logic & Correctness**
* **Collision Logic:** The collision detection is correct for AABB (Axis-Aligned Bounding Boxes).
* **Boundary Handling:** Player movement is correctly clamped to the screen dimensions.

**5. Performance & Security**
* **Resource Management:** As mentioned in Modularity, calling `pygame.font.SysFont` inside the main loop is a performance bottleneck. Move it to the initialization phase.

**6. Documentation & Testing**
* **Missing Documentation:** There are no docstrings or comments explaining the purpose of the functions.
* **Testing:** No unit tests are provided for the collision or movement logic.

### Summary of Improvements
* **Refactor Globals:** Move game state into a class to eliminate `global` keywords.
* **Standardize Naming:** Convert `camelCase` variables and functions to `snake_case`.
* **Optimize Rendering:** Move font initialization out of the `drawEverything` loop.
* **PEP 8:** Expand single-line `if` statements to multiple lines.