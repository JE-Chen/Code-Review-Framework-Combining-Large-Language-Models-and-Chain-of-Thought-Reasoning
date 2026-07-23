- Code Smell Type: Excessive Use of Global State
- Problem Location: `playerX`, `playerY`, `vx`, `vy`, `enemyList`, `scoreValue`, `runningGame`, and the `global` keywords inside `initGame`, `movePlayer`, `drawEverything`, `checkCollision`, and `mainLoop`.
- Detailed Explanation: The application relies entirely on global variables to manage state. This creates tight coupling between functions, making the code difficult to test in isolation and prone to side-effect bugs. As the game grows (e.g., adding levels or multiple players), managing state via globals becomes unsustainable and leads to "spaghetti code."
- Improvement Suggestions: Encapsulate the game state into a `Game` class or a `GameState` data object. Pass this object as an argument to functions or make the functions methods of the class.
- Priority Level: High

- Code Smell Type: Lack of Object-Oriented Abstraction (Primitive Obsession)
- Problem Location: `enemyList = []` and the logic in `drawEverything` and `checkCollision` (e.g., `e[0]`, `e[1]`).
- Detailed Explanation: Enemies are represented as simple lists of integers. This forces the developer to remember that index `0` is X and index `1` is Y, which reduces readability and increases the likelihood of indexing errors. It also makes it difficult to add enemy-specific properties (like speed or health) in the future.
- Improvement Suggestions: Create an `Enemy` class and a `Player` class. Use named attributes (e.g., `enemy.x`, `enemy.y`) and leverage `pygame.Rect` for collision detection and positioning.
- Priority Level: Medium

- Code Smell Type: Magic Numbers
- Problem Location: `drawEverything()` -> `screen.fill((0, 0, 0))`, `(0, 255, 0)`, `(255, 0, 0)`, `(255, 255, 255)`, and `(10, 10)`.
- Detailed Explanation: Hardcoded RGB tuples and coordinate offsets are used throughout the drawing logic. If the visual theme needs to change, the developer must hunt through the logic to find every instance of a color.
- Improvement Suggestions: Define constants at the top of the file for colors (e.g., `COLOR_BLACK = (0, 0, 0)`, `COLOR_PLAYER = (0, 255, 0)`) and UI offsets.
- Priority Level: Low