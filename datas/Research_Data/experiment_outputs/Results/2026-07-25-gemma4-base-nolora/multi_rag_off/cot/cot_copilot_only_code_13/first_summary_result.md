This code review is conducted based on the provided global rules.

### 1. Readability & Consistency
*   **Formatting:** The code is generally clean, but there are instances of multiple statements on one line (e.g., `if playerX < 0: playerX = 0`). For better readability and consistency with PEP 8, these should be broken into two lines.
*   **Consistency:** The naming style is inconsistent. It mixes `camelCase` (`enemyList`, `scoreValue`, `runningGame`) with `UPPER_CASE` for constants and `snake_case` for some functions.

### 2. Naming Conventions
*   **Variable Naming:** Most names are descriptive, but `vx` and `vy` are slightly cryptic; `velocity_x` and `velocity_y` would be more explicit.
*   **Semantic Clarity:** `enemyList` is a list of lists (coordinates). A more descriptive name like `enemy_positions` would clarify that it stores coordinates rather than "Enemy" objects.

### 3. Software Engineering Standards
*   **Modularization (High Concern):** The code relies heavily on `global` variables (`global screen`, `global playerX`, etc.). This is a significant anti-pattern that makes the code difficult to test, maintain, and scale.
    *   *Recommendation:* Encapsulate the game state into a `Game` class or pass state variables as arguments to functions.
*   **Abstraction:** The collision logic and drawing logic are tightly coupled with global state. Moving the player and enemies into their own classes (e.g., a `Player` class and an `Enemy` class) would improve modularity.

### 4. Logic & Correctness
*   **Boundary Conditions:** The boundary checks for the player are correctly implemented, preventing the player from moving off-screen.
*   **Collision Logic:** The AABB (Axis-Aligned Bounding Box) collision detection is logically correct.
*   **Initialization:** The game initializes correctly and handles the `QUIT` event to prevent the application from hanging.

### 5. Performance & Security
*   **Performance:** 
    *   `pygame.font.SysFont(None, 36)` is called inside `drawEverything()`. Since `drawEverything` runs every frame (30 times per second), this creates unnecessary overhead by recreating the font object repeatedly.
    *   *Recommendation:* Initialize the font once in `initGame()` and reuse it.
*   **Security:** No significant security risks identified as this is a local standalone game.

### 6. Documentation & Testing
*   **Documentation:** The code lacks docstrings for functions and a high-level module description.
*   **Testing:** There are no unit tests provided. Because the logic is tied to global variables and Pygame's internal state, the current structure is very difficult to unit test without running the full game loop.

---

### Summary of Recommendations

| Category | Issue | Priority | Suggestion |
| :--- | :--- | :--- | :--- |
| **Architecture** | Excessive use of `global` | High | Refactor into a Class-based structure. |
| **Performance** | Font instantiation in loop | Medium | Move `SysFont` call to `initGame`. |
| **Style** | Inconsistent Naming | Low | Standardize on `snake_case` for variables/functions. |
| **Readability** | Inline `if` statements | Low | Expand `if` blocks to multiple lines. |