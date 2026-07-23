### Code Review

#### 1. Readability & Consistency
- **Formatting:** The code is generally clean, but there are instances of multiple statements on one line (e.g., `if playerX < 0: playerX = 0`). For better readability and consistency with PEP 8, these should be moved to new lines.
- **Consistency:** The naming style is inconsistent. It mixes `camelCase` (`playerX`, `enemyList`, `scoreValue`, `runningGame`) with `snake_case` (`initGame` is camel, but `mainLoop` is camel, while `pygame` constants are `UPPER_CASE`).

#### 2. Naming Conventions
- **Variable Names:** Names like `vx`, `vy`, and `e` are too cryptic. `vx` should be `velocity_x` or `delta_x`, and `e` should be `enemy`.
- **Function Names:** Following Python conventions (PEP 8), functions should use `snake_case` (e.g., `init_game`, `move_player`, `draw_everything`).

#### 3. Software Engineering Standards
- **Global State:** The code relies heavily on `global` variables (`global playerX, playerY, vx, vy`, etc.). This makes the code difficult to test, maintain, and scale. 
    - *Recommendation:* Encapsulate the game state into a `Game` class or pass state objects as arguments to functions.
- **Modularity:** The logic for "Enemy" is handled as a list of lists. Creating an `Enemy` class would allow for better abstraction and easier addition of new enemy behaviors in the future.
- **Hardcoded Values:** Colors (e.g., `(0, 255, 0)`) are hardcoded in the draw function. These should be defined as constants at the top of the file (e.g., `COLOR_PLAYER = (0, 255, 0)`).

#### 4. Logic & Correctness
- **Collision Logic:** The collision detection is correct for AABB (Axis-Aligned Bounding Boxes).
- **Boundary Handling:** Player boundaries are correctly clamped to the screen dimensions.

#### 5. Performance & Security
- **Resource Management:** `pygame.font.SysFont(None, 36)` is called inside `drawEverything()`, which runs 30 times per second. Creating a font object every frame is a performance bottleneck.
    - *Recommendation:* Initialize the font once in `initGame()` and reuse the object.

#### 6. Documentation & Testing
- **Documentation:** There are no docstrings or comments explaining the purpose of the functions.
- **Testing:** There are no unit tests for the collision logic or movement boundaries.

---

### Summary of Changes (PR Summary)

**Key Changes**
- Implemented a basic 2D game loop using Pygame.
- Added player movement with boundary clamping.
- Implemented a scoring system based on collisions with randomly spawned enemies.

**Impact Scope**
- New game engine implementation affecting all provided logic.

**Purpose of Changes**
- Initial implementation of a "Bad Smelly Game" prototype.

**Items to Confirm**
- Review the use of global variables and consider refactoring into a class-based structure.
- Verify the performance impact of font initialization within the main draw loop.