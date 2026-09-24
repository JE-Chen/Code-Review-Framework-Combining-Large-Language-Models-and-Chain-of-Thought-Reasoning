- Code Smell Type: Excessive Use of Global State
- Problem Location: `playerX`, `playerY`, `vx`, `vy`, `enemyList`, `scoreValue`, `runningGame`, and the `global` keywords inside `initGame`, `movePlayer`, `drawEverything`, `checkCollision`, and `mainLoop`.
- Detailed Explanation: The application relies entirely on global variables to manage game state. This creates tight coupling between functions, making the code difficult to test in isolation and prone to side-effect bugs. As the game grows, tracking which function modifies which global variable becomes a maintenance nightmare.
- Improvement Suggestions: Encapsulate the game state into a `Game` class or a state dictionary/dataclass. Pass this state as an argument to functions or make them methods of the class.
- Priority Level: High

- Code Smell Type: Poor Naming Conventions (CamelCase vs snake_case)
- Problem Location: `playerX`, `playerY`, `enemyList`, `scoreValue`, `runningGame`, `initGame`, `movePlayer`, `drawEverything`, `checkCollision`, `mainLoop`, `endGame`.
- Detailed Explanation: The code uses `camelCase` for variables and functions, which violates PEP 8 (the standard Python style guide) that prescribes `snake_case` for functions and variables. This reduces consistency with the broader Python ecosystem.
- Improvement Suggestions: Rename all functions and variables to use snake_case (e.g., `player_x`, `enemy_list`, `init_game`).
- Priority Level: Low

- Code Smell Type: Lack of Data Abstraction (Primitive Obsession)
- Problem Location: `enemyList.append([random.randint(...), random.randint(...)])` and the collision check `e[0]`, `e[1]`.
- Detailed Explanation: Enemies are represented as simple lists of integers. Using indices like `e[0]` and `e[1]` is opaque; it is not immediately clear that these represent X and Y coordinates. This makes the code fragile and harder to read.
- Improvement Suggestions: Use a `pygame.Rect` object or a simple `Enemy` class to represent enemies. This would allow the use of descriptive attributes (e.g., `enemy.x`) and leverage Pygame's built-in `colliderect` method for collision detection.
- Priority Level: Medium

- Code Smell Type: Magic Numbers
- Problem Location: `screen.fill((0, 0, 0))`, `(0, 255, 0)`, `(255, 0, 0)`, `(255, 255, 255)`, and `clock.tick(27)`.
- Detailed Explanation: Hardcoded RGB tuples and the frame rate (27) are "magic numbers." If the visual theme needs to change or the game speed needs adjustment, the developer must hunt through the logic to find these values.
- Improvement Suggestions: Define these as constants at the top of the file (e.g., `COLOR_BLACK = (0, 0, 0)`, `FPS = 60`).
- Priority Level: Low