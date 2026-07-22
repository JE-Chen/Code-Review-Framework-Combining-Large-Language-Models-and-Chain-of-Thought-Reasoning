This code review is conducted based on the provided global rules.

### 1. Readability & Consistency
- **Formatting:** The code is generally clean, but there are instances of multiple statements on one line (e.g., `if playerX < 0: playerX = 0`). For better readability and debugging, these should be moved to separate lines.
- **Consistency:** The naming style is inconsistent. It mixes `camelCase` (`playerX`, `enemyList`, `scoreValue`) with `UPPER_SNAKE_CASE` (`WIDTH`, `HEIGHT`).

### 2. Naming Conventions
- **Variable Names:** Most names are descriptive, but `vx` and `vy` (velocity) could be more explicit (e.g., `velocity_x`, `velocity_y`) to improve semantic clarity for junior developers.
- **Function Names:** `drawEverything` is a bit generic; `render_game_state` or `draw_frame` would be more professional.

### 3. Software Engineering Standards
- **Modularization (High Concern):** The code relies heavily on `global` variables (`global screen`, `global playerX`, etc.). This is a significant anti-pattern that makes the code difficult to test, maintain, and scale.
- **Abstraction:** The game state (player position, score, enemies) should be encapsulated into a class (e.g., `GameState` or `GameEngine`) rather than living in the global namespace.
- **Hardcoded Values:** While constants are used for sizes, the color tuples (e.g., `(0, 255, 0)`) are hardcoded inside the draw function. These should be defined as constants at the top (e.g., `COLOR_PLAYER = (0, 255, 0)`).

### 4. Logic & Correctness
- **Collision Logic:** The AABB (Axis-Aligned Bounding Box) collision logic is implemented correctly.
- **Boundary Handling:** Player movement is correctly clamped to the screen dimensions.
- **Resource Management:** The `pygame.font.SysFont` is called inside `drawEverything`. Since `drawEverything` runs 30 times per second, this creates a new font object every frame, which is inefficient and can lead to memory overhead. The font should be initialized once in `initGame`.

### 5. Performance & Security
- **Performance:** As mentioned above, moving `pygame.font.SysFont` out of the main loop is the primary performance optimization needed.
- **Security:** No external inputs are processed, so there are no immediate security risks.

### 6. Documentation & Testing
- **Documentation:** There are no docstrings or comments explaining the purpose of the functions.
- **Testing:** There are no unit tests. Because the logic is tied to global state and Pygame's internal loop, the current structure is nearly impossible to unit test without running the full GUI.

---

### Summary of Recommendations

| Category | Issue | Priority | Recommendation |
| :--- | :--- | :--- | :--- |
| **Architecture** | Excessive use of `global` | High | Encapsulate game state into a class. |
| **Performance** | Font initialization in loop | Medium | Move `SysFont` call to `initGame`. |
| **Style** | Inconsistent naming | Low | Standardize on `snake_case` for variables/functions. |
| **Readability** | Inline `if` statements | Low | Expand `if` blocks to multiple lines. |