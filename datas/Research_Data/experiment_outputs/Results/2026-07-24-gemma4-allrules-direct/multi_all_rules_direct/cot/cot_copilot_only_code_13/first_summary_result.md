### Pull Request Summary

*   **Key changes**: Implemented a basic 2D game using `pygame` featuring a player-controlled square, randomly spawned enemies, and a collision-based scoring system.
*   **Impact scope**: New game logic implementation including initialization, input handling, collision detection, and rendering.
*   **Purpose of changes**: Initial feature implementation of a simple game loop.

---

### Code Review

#### 1. Readability & Consistency
*   **Naming Conventions**: Variable names like `playerX`, `playerY`, `vx`, and `vy` use camelCase, which deviates from the Python standard (PEP 8) of using `snake_case` (e.g., `player_x`, `velocity_x`).
*   **Formatting**: Some `if` statements are written on a single line (e.g., `if playerX < 0: playerX = 0`). For better readability and consistency, these should be expanded to multiple lines.

#### 2. Software Engineering Standards
*   **Modularization**: The code relies heavily on `global` variables (e.g., `global screen`, `global playerX`). This creates tight coupling and makes the code difficult to test or extend.
    *   *Recommendation*: Encapsulate the game state into a `Game` class or a state dictionary passed between functions.
*   **Responsibility**: `drawEverything()` is handling both the rendering of game objects and the creation of the font/text object every frame.
    *   *Recommendation*: Initialize the font once in `initGame()` rather than recreating it 30 times per second.

#### 3. Logic & Correctness
*   **Collision Logic**: The collision detection is correct for AABB (Axis-Aligned Bounding Boxes).
*   **Boundary Handling**: Player movement is correctly clamped to the screen dimensions.

#### 4. Performance & Security
*   **Resource Management**: The `pygame.font.SysFont` call inside `drawEverything()` is a performance bottleneck. Creating a new font object every frame is computationally expensive and can lead to memory fragmentation.
*   **Input Validation**: Not applicable for this local keyboard-driven application.

#### 5. RAG Rules Compliance
*   **Shared Mutable State**: The code violates the rule regarding shared mutable state at the module level. `enemyList`, `playerX`, and `scoreValue` are all global variables mutated across multiple functions. This makes the behavior harder to reason about.
*   **Single Responsibility**: `checkCollision()` is performing two distinct tasks: detecting a collision and resetting the enemy position (transformation). These should be separated.
*   **Magic Numbers**: While some constants are defined (e.g., `WIDTH`), colors like `(0, 255, 0)` and `(255, 0, 0)` are hard-coded "magic" tuples.
    *   *Recommendation*: Define colors as constants (e.g., `COLOR_PLAYER = (0, 255, 0)`).

#### 6. Documentation & Testing
*   **Documentation**: There are no docstrings or comments explaining the purpose of the functions.
*   **Testing**: There are no unit tests for the collision logic or movement clamping.

### Final Score & Summary
The code is a functional prototype but suffers from significant architectural issues, primarily the over-reliance on global state and inefficient resource handling in the render loop. Refactoring into a class-based structure and moving font initialization out of the main loop are the highest priority improvements.