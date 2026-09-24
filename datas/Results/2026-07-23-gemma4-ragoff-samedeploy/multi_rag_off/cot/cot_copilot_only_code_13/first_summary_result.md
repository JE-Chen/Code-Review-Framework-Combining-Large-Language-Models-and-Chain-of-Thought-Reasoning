This code review is conducted based on the provided global rules.

### 1. Readability & Consistency
- **Formatting:** The code is generally clean, but there are instances of multiple statements on one line (e.g., `if playerX < 0: playerX = 0`). For better readability and consistency with PEP 8, these should be moved to new lines.
- **Consistency:** The naming style is inconsistent. It mixes `camelCase` (`enemyList`, `scoreValue`, `runningGame`) with `snake_case` (`initGame` is camelCase, but `mainLoop` is also camelCase, while `PLAYER_SIZE` is UPPER_CASE). Python standard (PEP 8) suggests `snake_case` for functions and variables.

### 2. Naming Conventions
- **Descriptive Names:** Most names are clear, but `e` in `for e in enemyList` is too generic. `enemy` would be more descriptive.
- **Semantic Clarity:** `vx` and `vy` are acceptable for velocity, but `velocity_x` and `velocity_y` would be more explicit.

### 3. Software Engineering Standards
- **Modularization:** The code relies heavily on `global` variables (e.g., `global screen`, `global playerX`). This makes the code difficult to test, maintain, and scale. 
    - **Recommendation:** Encapsulate the game state into a `Game` class or pass state objects as arguments to functions.
- **Hardcoded Values:** Colors (e.g., `(0, 255, 0)`) are hardcoded inside the `drawEverything` function. These should be defined as constants at the top of the file (e.g., `COLOR_PLAYER = (0, 255, 0)`).
- **Resource Management:** The `font` object is created every single frame inside `drawEverything`. This is inefficient and can lead to performance degradation.
    - **Recommendation:** Initialize the font once in `initGame`.

### 4. Logic & Correctness
- **Collision Logic:** The AABB collision detection is implemented correctly.
- **Boundary Handling:** Player movement is correctly clamped to the screen dimensions.
- **Game Loop:** The loop correctly handles the `QUIT` event and maintains a steady framerate via `clock.tick(30)`.

### 5. Performance & Security
- **Performance Bottleneck:** As mentioned in section 3, calling `pygame.font.SysFont(None, 36)` 30 times per second is a significant performance waste.
- **Security:** No external inputs are processed, so there are no immediate security risks.

### 6. Documentation & Testing
- **Documentation:** The code lacks docstrings for functions and a high-level module description.
- **Testing:** There are no unit tests for the collision logic or movement constraints.

---

### Summary of Recommendations

| Category | Issue | Priority | Suggestion |
| :--- | :--- | :--- | :--- |
| **Architecture** | Excessive use of `global` | High | Use a Class to manage game state. |
| **Performance** | Font initialization in loop | High | Move `pygame.font.SysFont` to `initGame`. |
| **Style** | Inconsistent naming | Medium | Convert `camelCase` to `snake_case` per PEP 8. |
| **Readability** | Inline `if` statements | Low | Expand `if` blocks to multiple lines. |
| **Maintainability** | Hardcoded colors | Low | Define colors as constants. |