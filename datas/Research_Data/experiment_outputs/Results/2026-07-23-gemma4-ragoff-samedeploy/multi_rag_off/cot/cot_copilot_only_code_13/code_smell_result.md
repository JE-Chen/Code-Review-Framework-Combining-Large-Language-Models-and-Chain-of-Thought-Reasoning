- Code Smell Type: Excessive Use of Global State
- Problem Location: `playerX`, `playerY`, `vx`, `vy`, `enemyList`, `scoreValue`, `runningGame`, and the `global` keywords inside `initGame`, `movePlayer`, `drawEverything`, `checkCollision`, and `mainLoop`.
- Detailed Explanation: The application relies entirely on global variables to manage state. This creates tight coupling between functions, making the code difficult to test in isolation and prone to side-effect bugs. As the game grows (e.g., adding levels or multiple players), managing state via globals becomes unsustainable and leads to "spaghetti code."
- Improvement Suggestions: Encapsulate the game state into a `Game` class or a `GameState` data object. Pass this object as an argument to functions or make the functions methods of the class.
- Priority Level: High

- Code Smell Type: Lack of Data Abstraction (Primitive Obsession)
- Problem Location: `enemyList = []` and the usage of `e[0]`, `e[1]` in `drawEverything` and `checkCollision`.
- Detailed Explanation: Enemies are represented as simple lists of integers. Using indices like `e[0]` and `e[1]` is non-descriptive and error-prone; it is not immediately clear that index 0 is X and index 1 is Y. This reduces readability and makes it harder to add new properties to enemies (e.g., speed or health).
- Improvement Suggestions: Create an `Enemy` class or use `pygame.Rect` objects. `pygame.Rect` is specifically designed for this purpose and provides built-in collision detection methods (e.g., `colliderect`), which would simplify the logic.
- Priority Level: Medium

- Code Smell Type: Violation of Single Responsibility Principle (SRP)
- Problem Location: `drawEverything()`
- Detailed Explanation: This function is responsible for clearing the screen, drawing the player, drawing all enemies, rendering the UI text, and updating the display. Mixing game object rendering with UI rendering and display flipping makes the function a "God Function" for visuals.
- Improvement Suggestions: Split the function into smaller, specialized functions: `draw_player()`, `draw_enemies()`, and `draw_ui()`.
- Priority Level: Low