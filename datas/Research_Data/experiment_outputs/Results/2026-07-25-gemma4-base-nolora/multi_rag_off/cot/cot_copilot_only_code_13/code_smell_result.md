- Code Smell Type: Excessive Use of Global State
- Problem Location: `playerX`, `playerY`, `vx`, `vy`, `enemyList`, `scoreValue`, `runningGame`, and the `global` keywords inside `initGame`, `movePlayer`, `drawEverything`, `checkCollision`, and `mainLoop`.
- Detailed Explanation: The application relies almost entirely on global variables to manage state. This creates tight coupling between functions, making the code difficult to test in isolation and prone to side-effect bugs. As the game grows (e.g., adding multiple levels or a main menu), managing this state will become unsustainable and lead to "spaghetti code."
- Improvement Suggestions: Encapsulate the game state into a `Game` class or separate `Player` and `Enemy` classes. Pass these objects as arguments to functions or maintain them as instance attributes.
- Priority Level: High

- Code Smell Type: Violation of Single Responsibility Principle (SRP)
- Problem Location: `drawEverything()`
- Detailed Explanation: This function is handling three distinct responsibilities: clearing the screen, rendering game objects (player and enemies), and rendering the UI (score text). Mixing game logic/rendering with UI logic makes it harder to modify the visual style or add a separate UI layer without risking the core rendering loop.
- Improvement Suggestions: Split this into smaller functions: `clear_screen()`, `draw_entities()`, and `draw_ui()`.
- Priority Level: Medium

- Code Smell Type: Unclear Naming & Data Structure (Primitive Obsession)
- Problem Location: `enemyList` and the loop `for e in enemyList: ... e[0], e[1]`
- Detailed Explanation: `enemyList` is a list of lists, where indices `0` and `1` implicitly represent X and Y coordinates. This is "Primitive Obsession." Using raw indices (`e[0]`) reduces readability and increases the likelihood of errors (e.g., accidentally swapping X and Y).
- Improvement Suggestions: Use `pygame.Rect` objects for enemies and the player. `pygame.Rect` provides built-in methods for movement and collision detection (e.g., `colliderect()`), which would also simplify the logic in `checkCollision`.
- Priority Level: Medium

- Code Smell Type: Magic Numbers
- Problem Location: `initGame()` -> `range(7)` and `drawEverything()` -> `(0, 0, 0)`, `(0, 255, 0)`, `(255, 0, 0)`, `(255, 255, 255)`, `(10, 10)`.
- Detailed Explanation: The number of enemies (7) and the RGB color tuples are hardcoded directly into the logic. If you want to change the theme of the game or the difficulty, you have to hunt through the function bodies rather than updating a configuration section at the top.
- Improvement Suggestions: Define constants at the top of the file, such as `ENEMY_COUNT = 7`, `COLOR_BLACK = (0, 0, 0)`, `COLOR_PLAYER = (0, 255, 0)`, etc.
- Priority Level: Low