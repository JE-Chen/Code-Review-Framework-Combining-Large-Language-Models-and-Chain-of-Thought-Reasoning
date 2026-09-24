## PR Summary

*   **Key changes**: Implemented a basic Pygame application featuring a controllable player square, randomly spawned enemy squares, and a collision-based scoring system.
*   **Impact scope**: New file `game.py`.
*   **Purpose of changes**: Initial implementation of a simple game prototype.
*   **Items to confirm**: Review the use of global state and the overall architectural structure for future scalability.

---

## Code Review

### 1. Readability & Consistency
*   **Naming Conventions**: The codebase uses a mix of `camelCase` (`playerX`, `enemyList`, `scoreValue`, `initGame`) and `UPPER_CASE` for constants. Python (PEP 8) standard is `snake_case` for variables and functions.
*   **Formatting**: Some conditional statements are written on a single line (e.g., `if playerX < 0: playerX = 0`), which reduces readability. It is recommended to move the action to a new indented line.

### 2. Software Engineering Standards
*   **Modularity**: The code is written as a procedural script. All game state is stored in global variables, which makes the code difficult to maintain and scale.
*   **Abstraction**: The player and enemies are handled as raw coordinates/lists. Encapsulating these into classes (e.g., `Player` and `Enemy`) would improve organization and allow for easier addition of new behaviors.

### 3. Logic & Correctness
*   **Collision Logic**: The collision detection is correct for AABB (Axis-Aligned Bounding Boxes).
*   **Boundary Checks**: Player movement is correctly clamped to the screen dimensions.

### 4. Performance & Security
*   **Resource Management**: `pygame.font.SysFont(None, 36)` is called inside `drawEverything()`. Since `drawEverything` runs every frame (approx. 27 times per second), this creates unnecessary overhead by recreating the font object repeatedly. The font should be initialized once in `initGame()`.

### 5. RAG Rules Violations (Critical)
*   **Shared Mutable State**: The code relies heavily on `global` variables (`playerX`, `playerY`, `enemyList`, `scoreValue`, `runningGame`). This violates the rule: *"Be careful with shared mutable state at the module or class level... Prefer passing state explicitly or encapsulating it in well-defined objects."*
*   **Testability**: Because the logic is tightly coupled to global state and the `pygame` display loop, it is nearly impossible to unit test `movePlayer` or `checkCollision` without initializing a full GUI environment. This violates the rule: *"Tightly coupled code, hidden dependencies, and heavy use of globals make unit testing difficult and brittle."*

### Summary of Recommendations
1.  **Refactor to OOP**: Create a `Game` class to encapsulate the state (score, player, enemies) and methods.
2.  **Fix Font Initialization**: Move `pygame.font.SysFont` out of the main loop.
3.  **Standardize Naming**: Convert `camelCase` to `snake_case` to align with Python standards.
4.  **Remove Globals**: Pass state as arguments to functions or store them as instance attributes.