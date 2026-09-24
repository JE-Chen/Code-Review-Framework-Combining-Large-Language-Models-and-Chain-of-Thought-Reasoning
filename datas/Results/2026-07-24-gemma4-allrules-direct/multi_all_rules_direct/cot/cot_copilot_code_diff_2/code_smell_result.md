- Code Smell Type: Shared Mutable State (Global Variables)
- Problem Location: `screen`, `playerX`, `playerY`, `vx`, `vy`, `enemyList`, `scoreValue`, `runningGame`
- Detailed Explanation: The code relies heavily on global variables and the `global` keyword across almost every function. This creates hidden coupling between functions, making the code difficult to reason about, test, and scale. For example, `movePlayer` and `checkCollision` directly mutate global state, which can lead to unpredictable behavior as the project grows.
- Improvement Suggestions: Encapsulate the game state into a `Game` class or a state dictionary/dataclass. Pass this state explicitly to functions as arguments or manage it as instance attributes.
- Priority Level: High

- Code Smell Type: Violation of Single Responsibility Principle (SRP)
- Problem Location: `drawEverything()`
- Detailed Explanation: This function is responsible for clearing the screen, drawing the player, drawing all enemies, rendering the UI text, and updating the display. Mixing game object rendering with UI rendering and display management makes the function harder to maintain and modify (e.g., if you wanted to change the UI layout without touching the game object logic).
- Improvement Suggestions: Split the function into smaller, focused functions: `draw_player()`, `draw_enemies()`, `draw_ui()`, and a coordinator function that handles the `screen.fill` and `pygame.display.flip()`.
- Priority Level: Medium

- Code Smell Type: Unclear Naming & Lack of Type Safety
- Problem Location: `enemyList` and the loop `for e in enemyList:`
- Detailed Explanation: `enemyList` stores enemies as simple lists of coordinates `[x, y]`. Accessing them via indices (`e[0]`, `e[1]`) is opaque and error-prone. It is not immediately clear what `e[0]` represents without tracing the initialization logic.
- Improvement Suggestions: Use a `pygame.Rect` object or a simple `Enemy` class/namedtuple to store coordinates. This allows for more readable code (e.g., `enemy.x` instead of `e[0]`) and enables the use of built-in Pygame collision methods like `colliderect()`.
- Priority Level: Medium

- Code Smell Type: Magic Numbers
- Problem Location: `drawEverything()` (colors) and `mainLoop()` (`clock.tick(27)`)
- Detailed Explanation: Colors like `(0, 255, 0)` and the frame rate `27` are hard-coded. If these need to be changed across the game, it requires searching and replacing multiple instances. The number `27` is particularly arbitrary and lacks a descriptive name.
- Improvement Suggestions: Define named constants at the top of the file, such as `COLOR_PLAYER = (0, 255, 0)`, `COLOR_ENEMY = (255, 0, 0)`, and `FPS = 27`.
- Priority Level: Low