- Code Smell Type: Shared Mutable State (Global Variables)
- Problem Location: `screen`, `playerX`, `playerY`, `vx`, `vy`, `enemyList`, `scoreValue`, `runningGame`
- Detailed Explanation: The application relies heavily on global variables and the `global` keyword across almost every function. This creates hidden coupling between functions, making the code difficult to reason about, test, and scale. For example, `checkCollision` and `movePlayer` both mutate global state, meaning the order of execution and the current state of the global environment are critical and fragile.
- Improvement Suggestions: Encapsulate the game state into a `Game` class or a state dictionary/dataclass. Pass this state object as an argument to functions or define the functions as methods within a class.
- Priority Level: High

- Code Smell Type: Violation of Single Responsibility Principle (SRP)
- Problem Location: `drawEverything()`
- Detailed Explanation: This function is handling multiple responsibilities: clearing the screen, rendering the player, rendering the enemies, initializing a font object, rendering text, and flipping the display. Mixing resource initialization (font creation) with rendering logic inside a loop is inefficient and reduces modularity.
- Improvement Suggestions: Split the function into smaller, focused methods: `draw_player()`, `draw_enemies()`, and `draw_ui()`. Initialize the font once in `initGame()` rather than every frame.
- Priority Level: Medium

- Code Smell Type: Magic Numbers
- Problem Location: `drawEverything()` (e.g., `(0, 0, 0)`, `(0, 255, 0)`, `(255, 0, 0)`, `(10, 10)`) and `initGame()` (`range(7)`)
- Detailed Explanation: Hard-coded colors and coordinates are scattered throughout the logic. If the team decides to change the background color or the number of enemies, they must hunt through the implementation details rather than updating a configuration section.
- Improvement Suggestions: Define named constants at the top of the file (e.g., `COLOR_BLACK = (0, 0, 0)`, `NUM_ENEMIES = 7`, `UI_OFFSET = (10, 10)`).
- Priority Level: Low

- Code Smell Type: Unclear Naming / Lack of Type Safety
- Problem Location: `enemyList` and the loop `for e in enemyList:`
- Detailed Explanation: `enemyList` stores enemies as simple lists of coordinates `[x, y]`. Accessing them via `e[0]` and `e[1]` is non-descriptive and error-prone. It is not immediately clear what index 0 or 1 represents without tracing the initialization logic.
- Improvement Suggestions: Use a `pygame.Rect` object or a simple `Enemy` class/namedtuple to store enemy positions. This allows for more readable code like `enemy.x` or `enemy.rect.colliderect(player_rect)`.
- Priority Level: Medium