- Code Smell Type: Excessive Use of Global State
- Problem Location: `playerX`, `playerY`, `vx`, `vy`, `enemyList`, `scoreValue`, `runningGame` and the corresponding `global` keywords inside `initGame`, `movePlayer`, `drawEverything`, `checkCollision`, and `mainLoop`.
- Detailed Explanation: The application relies entirely on global variables to manage state. This creates tight coupling between functions, making the code difficult to test in isolation and prone to side-effect bugs. As the game grows (e.g., adding multiple levels or a main menu), managing state via globals becomes unsustainable and leads to "spaghetti code."
- Improvement Suggestions: Encapsulate the game state into a `Game` class or a `GameState` data structure. Pass this object as an argument to functions or make the functions methods of the class.
- Priority Level: High

- Code Smell Type: Poor Data Modeling (Primitive Obsession)
- Problem Location: `enemyList.append([random.randint(...), random.randint(...)])` and `e[0]`, `e[1]` in `drawEverything` and `checkCollision`.
- Detailed Explanation: Enemies are represented as simple lists of integers. Using indices like `e[0]` and `e[1]` to represent X and Y coordinates is non-descriptive and error-prone. It forces the developer to remember the order of elements rather than using named attributes.
- Improvement Suggestions: Create an `Enemy` class or use `pygame.Rect` objects. `pygame.Rect` is specifically designed for this purpose and provides built-in collision detection methods (e.g., `colliderect`), which would also simplify the logic in `checkCollision`.
- Priority Level: Medium

- Code Smell Type: Violation of Single Responsibility Principle (SRP)
- Problem Location: `drawEverything()`
- Detailed Explanation: This function is responsible for clearing the screen, drawing the player, drawing all enemies, rendering the UI text, and flipping the display. It mixes game logic (iterating through enemies) with low-level rendering and UI management.
- Improvement Suggestions: Split this into smaller functions: `draw_player()`, `draw_enemies()`, and `draw_ui()`. A coordinator function can then call these in order.
- Priority Level: Low