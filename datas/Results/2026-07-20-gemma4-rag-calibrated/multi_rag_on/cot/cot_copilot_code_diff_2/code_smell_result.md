- Code Smell Type: Shared Mutable State / Heavy Use of Globals
- Problem Location: Lines 5-12 and the `global` keywords inside `initGame`, `movePlayer`, `drawEverything`, `checkCollision`, and `mainLoop`.
- Detailed Explanation: The code relies heavily on global variables (`playerX`, `playerY`, `enemyList`, `scoreValue`, etc.) to maintain game state. This creates tight coupling between functions and makes the code difficult to test, as the state persists across function calls and cannot be easily reset or isolated for unit testing. It violates the RAG rule regarding shared mutable state at the module level.
- Improvement Suggestions: Encapsulate the game state within a `Game` class or a state object. Pass this object as an argument to functions or make the functions methods of the class.
- Priority Level: High

- Code Smell Type: Unclear Naming / Inconsistent Naming Conventions
- Problem Location: `playerX`, `playerY`, `vx`, `vy`, `enemyList`, `scoreValue`, `runningGame`, `initGame`, `movePlayer`, etc.
- Detailed Explanation: The codebase uses a mix of camelCase (`playerX`, `enemyList`) and lowercase/snake_case. According to PEP 8 (the standard for Python), variables and functions should use `snake_case`. Additionally, `vx` and `vy` are overly concise; while common in physics, `velocity_x` and `velocity_y` are more descriptive.
- Improvement Suggestions: Rename all variables and functions to follow `snake_case` (e.g., `player_x`, `enemy_list`, `init_game`).
- Priority Level: Low

- Code Smell Type: Magic Numbers
- Problem Location: `drawEverything()` (lines 53-56) and `mainLoop()` (line 76).
- Detailed Explanation: The code uses hard-coded tuples for colors (e.g., `(0, 255, 0)`, `(255, 0, 0)`) and a hard-coded frame rate (`clock.tick(27)`). This makes it difficult to change the visual theme or adjust game performance globally without searching through the logic.
- Improvement Suggestions: Define named constants at the top of the file, such as `COLOR_PLAYER = (0, 255, 0)`, `COLOR_ENEMY = (255, 0, 0)`, and `FPS = 27`.
- Priority Level: Medium

- Code Smell Type: Violation of Single Responsibility Principle (SRP)
- Problem Location: `drawEverything()`
- Detailed Explanation: This function is responsible for clearing the screen, drawing the player, drawing all enemies, rendering the UI text, and flipping the display. It mixes game logic (rendering different entities) with system-level display updates.
- Improvement Suggestions: Split the function into smaller, specialized functions: `draw_player()`, `draw_enemies()`, and `draw_ui()`.
- Priority Level: Medium