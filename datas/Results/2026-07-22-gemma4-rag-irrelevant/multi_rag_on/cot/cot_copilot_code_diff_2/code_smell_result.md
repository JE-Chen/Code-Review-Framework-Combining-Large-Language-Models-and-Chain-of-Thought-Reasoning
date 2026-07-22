- Code Smell Type: Excessive Use of Global State
- Problem Location: `playerX`, `playerY`, `vx`, `vy`, `enemyList`, `scoreValue`, `runningGame`, and the `global` keywords inside `initGame`, `movePlayer`, `drawEverything`, `checkCollision`, and `mainLoop`.
- Detailed Explanation: The application relies entirely on global variables to manage game state. This creates tight coupling between functions, making the code difficult to test in isolation and prone to side-effect bugs. As the game grows, tracking which function modifies which global variable becomes a maintenance nightmare.
- Improvement Suggestions: Encapsulate the game state into a `Game` class or a `GameState` data object. Pass this object as an argument to functions or make the functions methods of the class.
- Priority Level: High

- Code Smell Type: Poor Naming Conventions (Inconsistent Casing)
- Problem Location: `playerX`, `playerY`, `enemyList`, `scoreValue`, `runningGame` (camelCase) vs `WIDTH`, `HEIGHT` (UPPER_CASE) and `initGame`, `movePlayer` (camelCase).
- Detailed Explanation: The code mixes camelCase for variables and functions, which violates PEP 8 (the standard Python style guide). Python conventions dictate `snake_case` for functions and variables. This inconsistency reduces readability and professional quality.
- Improvement Suggestions: Rename variables and functions to use snake_case (e.g., `player_x`, `enemy_list`, `init_game`, `move_player`).
- Priority Level: Medium

- Code Smell Type: Primitive Obsession / Lack of Domain Modeling
- Problem Location: `enemyList.append([random.randint(...), random.randint(...)])` and `e[0]`, `e[1]` in `drawEverything` and `checkCollision`.
- Detailed Explanation: Enemies are represented as simple lists of integers. Using indices like `e[0]` and `e[1]` is opaque; it is not immediately clear that index 0 is X and index 1 is Y. This makes the code fragile and harder to extend (e.g., if you wanted to add enemy health or speed).
- Improvement Suggestions: Create a `Player` and `Enemy` class (or use `pygame.Rect` objects), which provide named attributes and built-in collision detection methods (like `colliderect`).
- Priority Level: Medium

- Code Smell Type: Magic Numbers
- Problem Location: `for i in range(9):` in `initGame()` and `clock.tick(27)` in `mainLoop()`.
- Detailed Explanation: The number of enemies (9) and the frame rate (27) are hardcoded as "magic numbers." A developer looking at the code cannot immediately tell why these specific values were chosen or where to change them to balance the game.
- Improvement Suggestions: Define these as named constants at the top of the file, e.g., `ENEMY_COUNT = 9` and `FPS = 27`.
- Priority Level: Low