## PR Summary

- **Key changes**: Implemented a basic Pygame application featuring a controllable player square, randomly spawned enemy squares, and a collision-based scoring system.
- **Impact scope**: New file `game.py`.
- **Purpose of changes**: Initial implementation of game logic and rendering.
- **Items to confirm**: Review the use of global state and overall architectural structure for future scalability.

---

## Code Review

### 1. Readability & Consistency
- **Formatting**: The code is generally clean, but some conditional blocks are written on a single line (e.g., `if playerX < 0: playerX = 0`), which deviates from PEP 8 standards. These should be expanded to separate lines for better readability.

### 2. Naming Conventions
- **Variable Naming**: The codebase uses a mix of `camelCase` (`playerX`, `enemyList`, `scoreValue`, `runningGame`) and `snake_case` (standard for Python). To follow Python conventions (PEP 8), these should be renamed to `player_x`, `enemy_list`, etc.

### 3. Software Engineering Standards
- **Modularity**: The code is written as a script with functions relying on global state. This makes the code difficult to maintain and extend.
- **Recommendation**: Encapsulate the game state into a `Game` class or a `GameState` object. This would remove the need for `global` keywords and allow for easier resets or multiple game levels.

### 4. Logic & Correctness
- **Collision Logic**: The collision detection is correct for AABB (Axis-Aligned Bounding Boxes).
- **Boundary Checks**: Player movement is correctly clamped to the screen dimensions.

### 5. Performance & Security
- **Resource Management**: `pygame.font.SysFont(None, 36)` is called inside `drawEverything()`. Since `drawEverything` runs every frame (approx. 27 times per second), creating a new font object repeatedly is inefficient.
- **Recommendation**: Initialize the font once in `initGame()` and store it in a variable.

### 6. Documentation & Testing
- **Documentation**: There are no docstrings or comments explaining the purpose of the functions.
- **Testing**: The code is currently untestable via unit tests because the logic is tightly coupled with the Pygame display and global variables.

### 7. RAG Rules Compliance
- **Shared Mutable State**: ❌ **Violation**. The code relies heavily on global variables (`playerX`, `playerY`, `enemyList`, `scoreValue`). This introduces hidden coupling and makes the code brittle.
- **Testability**: ❌ **Violation**. Because the logic is tied to global state and direct Pygame calls, it is impossible to test `movePlayer` or `checkCollision` without initializing a full Pygame window.
- **Magic Numbers**: ✅ **Partial**. While `WIDTH`, `HEIGHT`, and `SPEED` are defined as constants, the colors (e.g., `(0, 255, 0)`) and the clock tick rate (`27`) are hard-coded. These should be moved to named constants (e.g., `COLOR_PLAYER = (0, 255, 0)`).

---

### Final Score & Summary
The code is a functional prototype but suffers from significant architectural issues regarding state management and Pythonic conventions. The heavy use of globals and the lack of encapsulation make it difficult to test and maintain.

**Key Action Items:**
1. Refactor global variables into a class.
2. Move font initialization out of the main loop.
3. Update naming conventions to `snake_case`.
4. Define colors and frame rates as constants.