### PR Summary

- **Key changes**: Implemented a basic Pygame application featuring a controllable player square, randomly spawned enemy squares, and a collision-based scoring system.
- **Impact scope**: New file `game.py`.
- **Purpose of changes**: Initial implementation of game logic and rendering loop.
- **Items to confirm**: Review the use of global state and the fixed frame rate (27 FPS).

---

### Code Review

#### 1. Readability & Consistency
- **Formatting**: The code is generally clean, but there are instances of multiple statements on one line (e.g., `if playerX < 0: playerX = 0`). For better readability and consistency with PEP 8, these should be moved to new lines.

#### 2. Naming Conventions
- **Variable Naming**: The codebase uses a mix of `camelCase` (`playerX`, `enemyList`, `scoreValue`, `runningGame`) and `snake_case` (implied by Pygame's API). According to Python (PEP 8) standards, variables and functions should use `snake_case` (e.g., `player_x`, `enemy_list`).
- **Constants**: `WIDTH`, `HEIGHT`, etc., are correctly named in `UPPER_CASE`.

#### 3. Software Engineering Standards
- **Modularization**: The code relies heavily on `global` variables (e.g., `global screen`, `global playerX`). This makes the code difficult to test and maintain. 
    - *Recommendation*: Encapsulate the game state into a class (e.g., `GameState`) or pass parameters into functions.
- **Data Structures**: `enemyList` stores enemies as lists `[x, y]`. Using a `pygame.Rect` object or a named tuple would be more semantic and provide built-in collision methods.

#### 4. Logic & Correctness
- **Collision Logic**: The collision detection is manually implemented. While correct, `pygame.Rect.colliderect()` is the standard, more readable way to handle this in Pygame.
- **Boundary Conditions**: Player boundaries are correctly clamped to the screen dimensions.

#### 5. Performance & Security
- **Resource Management**: `pygame.font.SysFont(None, 36)` is called inside `drawEverything()`. This means a new font object is created every single frame (27 times per second), which is a significant performance bottleneck.
    - *Recommendation*: Initialize the font once in `initGame()` and reuse it.

#### 6. Documentation & Testing
- **Documentation**: There are no docstrings or comments explaining the purpose of the functions.
- **Testing**: No unit tests are provided for the collision logic or movement constraints.

### Summary of Issues
| Severity | Category | Description |
| :--- | :--- | :--- |
| 🔴 High | Performance | Font object created every frame in `drawEverything`. |
| 🟡 Medium | Engineering | Excessive use of `global` variables; lack of encapsulation. |
| 🟡 Medium | Naming | Inconsistent naming convention (camelCase vs snake_case). |
| 🔵 Low | Readability | Inline `if` statements should be expanded. |