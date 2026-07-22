- Code Smell Type: Excessive Use of Global State
- Problem Location: `playerX`, `playerY`, `vx`, `vy`, `enemyList`, `scoreValue`, `runningGame`, and the `global` keywords inside `initGame`, `movePlayer`, `drawEverything`, `checkCollision`, and `mainLoop`.
- Detailed Explanation: The code relies heavily on global variables to manage game state. This creates tight coupling between functions and makes the code difficult to test, debug, and scale. For example, `movePlayer` and `checkCollision` directly modify global coordinates and scores, making it impossible to run multiple game instances or reset the game state without manually resetting every global variable.
- Improvement Suggestions: Encapsulate the game state into a `Game` class or a `GameState` data structure. Pass this state as an argument to functions or make them methods of a class.
- Priority Level: High

- Code Smell Type: Poor Naming Conventions (Inconsistent Casing)
- Problem Location: `playerX`, `playerY`, `enemyList`, `scoreValue`, `runningGame` (camelCase) vs `WIDTH`, `HEIGHT` (UPPER_CASE) and `initGame`, `movePlayer` (camelCase).
- Detailed Explanation: The code mixes camelCase for variables and functions, which deviates from the standard Python PEP 8 style guide (which recommends `snake_case` for functions and variables). This reduces readability for other Python developers and creates inconsistency within the codebase.
- Improvement Suggestions: Rename variables and functions to use `snake_case` (e.g., `player_x`, `enemy_list`, `init_game`, `move_player`).
- Priority Level: Low

- Code Smell Type: Lack of Data Abstraction (Primitive Obsession)
- Problem Location: `enemyList.append([random.randint(...), random.randint(...)])` and `e[0]`, `e[1]` in `drawEverything` and `checkCollision`.
- Detailed Explanation: Enemies are represented as simple lists of integers. Using indices like `e[0]` and `e[1]` to represent X and Y coordinates is opaque and error-prone. If the structure of an "enemy" needs to change (e.g., adding a speed or color), every index-based access across the codebase must be updated.
- Improvement Suggestions: Create a simple `Enemy` class or use `pygame.Rect` objects, which provide built-in collision detection methods (like `colliderect`) and named attributes (`x`, `y`, `width`, `height`).
- Priority Level: Medium