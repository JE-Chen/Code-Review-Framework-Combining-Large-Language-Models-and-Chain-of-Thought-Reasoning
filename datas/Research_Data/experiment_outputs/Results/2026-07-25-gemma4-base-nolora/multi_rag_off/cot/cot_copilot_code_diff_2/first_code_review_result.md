### Code Review

**Naming Conventions**
* **Case Consistency:** The codebase mixes `camelCase` (`playerX`, `enemyList`, `scoreValue`) with `snake_case` (standard for Python) and `UPPER_CASE` (constants). Suggest using `snake_case` for all variables and functions (e.g., `player_x`, `init_game`) to adhere to PEP 8.
* **Vague Naming:** `vx` and `vy` are acceptable for velocity, but `e` in the `drawEverything` and `checkCollision` loops should be renamed to `enemy` for better clarity.

**Software Engineering Standards**
* **Global State Overuse:** The code relies heavily on `global` variables. This makes the code harder to test and maintain. Suggest encapsulating the game state into a `Game` class or passing state as arguments to functions.
* **Hardcoded Values:** Colors (e.g., `(0, 255, 0)`) are hardcoded in the draw calls. These should be defined as constants at the top of the file (e.g., `COLOR_PLAYER = (0, 255, 0)`).
* **Resource Management:** The `font` object is created every single frame inside `drawEverything()`. This is inefficient; the font should be initialized once in `initGame()`.

**Logic & Correctness**
* **Boundary Handling:** The player boundary checks are implemented as single-line `if` statements (e.g., `if playerX < 0: playerX = 0`). While correct, standard formatting suggests placing the action on a new indented line for readability.

**Readability & Consistency**
* **Formatting:** The code is generally clean, but the lack of docstrings for functions makes the intent less explicit for new maintainers.

**Summary of Suggestions**
* Refactor global variables into a class or state object.
* Move `pygame.font.SysFont` initialization out of the main loop.
* Standardize naming to `snake_case`.
* Define colors as constants.