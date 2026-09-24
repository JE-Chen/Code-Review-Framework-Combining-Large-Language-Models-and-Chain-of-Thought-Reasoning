- Code Smell Type: Shared Mutable State (Global Variables)
- Problem Location: 
  ```python
  screen = None
  playerX = 100
  playerY = 100
  vx = 0
  vy = 0
  enemyList = []
  scoreValue = 0
  runningGame = True
  ```
  And subsequent use of `global` keywords in `initGame`, `movePlayer`, `drawEverything`, `checkCollision`, and `mainLoop`.
- Detailed Explanation: The code relies heavily on global variables to maintain the game state. This creates tight coupling between all functions and makes the code extremely difficult to test in isolation (unit testing). It also prevents the possibility of running multiple game instances or resetting the game state without manually resetting every global variable. This violates the RAG rule regarding shared mutable state at the module level.
- Improvement Suggestions: Encapsulate the game state within a `Game` class or a state dictionary/dataclass. Pass this state object as an argument to the functions that need it, or make the functions methods of the `Game` class.
- Priority Level: High

- Code Smell Type: Unclear Naming (Non-descriptive/Inconsistent)
- Problem Location: 
  - `vx`, `vy`
  - `enemyList` (Hungarian notation/type in name)
  - `e` (inside `drawEverything` and `checkCollision`)
- Detailed Explanation: `vx` and `vy` are overly concise; while common in physics, `velocity_x` and `velocity_y` are more descriptive. `enemyList` includes the type in the name, which is generally discouraged in Python (prefer `enemies`). The variable `e` in loops is too generic, reducing readability when scanning the logic.
- Improvement Suggestions: Rename `vx`/`vy` to `velocity_x`/`velocity_y`, `enemyList` to `enemies`, and `e` to `enemy`.
- Priority Level: Low

- Code Smell Type: Magic Numbers
- Problem Location: 
  - `for i in range(9):` (in `initGame`)
  - `screen.fill((0, 0, 0))`
  - `pygame.draw.rect(screen, (0, 255, 0), ...)`
  - `clock.tick(27)`
- Detailed Explanation: The number of enemies (9), the colors (RGB tuples), and the frame rate (27) are hard-coded directly into the logic. If these need to be changed or reused, the developer must hunt through the implementation details. This violates the RAG rule against magic numbers.
- Improvement Suggestions: Define these as named constants at the top of the file (e.g., `NUM_ENEMIES = 9`, `COLOR_BLACK = (0, 0, 0)`, `FPS = 27`).
- Priority Level: Medium

- Code Smell Type: Violation of Single Responsibility Principle (SRP)
- Problem Location: `drawEverything()`
- Detailed Explanation: This function is responsible for clearing the screen, drawing the player, drawing all enemies, rendering the UI text, and flipping the display. It mixes game object rendering with UI rendering and display management.
- Improvement Suggestions: Split this into smaller functions: `draw_player()`, `draw_enemies()`, and `draw_ui()`. A coordinator function can then call these in order.
- Priority Level: Medium