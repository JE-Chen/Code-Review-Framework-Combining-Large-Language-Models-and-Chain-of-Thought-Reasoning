- Code Smell Type: Excessive Use of Global State
- Problem Location: `playerX`, `playerY`, `vx`, `vy`, `enemyList`, `scoreValue`, `runningGame`, `screen` (and their corresponding `global` declarations inside functions).
- Detailed Explanation: The code relies heavily on global variables to maintain the game state. This creates tight coupling between functions, making the code difficult to test in isolation and prone to side-effect bugs. As the project grows, tracking which function modifies which global variable becomes a maintenance nightmare. It also prevents the possibility of running multiple game instances or resetting the game state cleanly without manually resetting every variable.
- Improvement Suggestions: Encapsulate the game state into a `Game` class or a `GameState` data structure. Pass this object as an argument to functions or make the functions methods of the class.
- Priority Level: High

- Code Smell Type: Violation of Single Responsibility Principle (SRP) / Lack of Abstraction
- Problem Location: `drawEverything()` and `checkCollision()`
- Detailed Explanation: The logic for "what a player is" and "what an enemy is" is scattered across multiple functions. For example, `drawEverything` handles the rendering of the player, the enemies, and the UI, while `checkCollision` handles the physics and the scoring logic. The enemies are represented as simple lists `[x, y]`, forcing other functions to use magic indices like `e[0]` and `e[1]`, which reduces readability and increases the risk of index errors.
- Improvement Suggestions: Create `Player` and `Enemy` classes. Move the drawing logic into a `.draw()` method and the collision/movement logic into respective methods within those classes.
- Priority Level: Medium

- Code Smell Type: Inconsistent Naming Conventions
- Problem Location: `playerX`, `playerY`, `enemyList`, `scoreValue`, `runningGame` vs `WIDTH`, `HEIGHT`, `PLAYER_SIZE`.
- Detailed Explanation: The codebase mixes `camelCase` (e.g., `enemyList`) with `snake_case` (implied by standard Python PEP 8 conventions) and `UPPER_CASE` for constants. In Python, the standard for variables and functions is `snake_case`. This inconsistency makes the code look unprofessional and reduces readability for other Python developers.
- Improvement Suggestions: Rename all variables and functions to follow PEP 8 guidelines (e.g., `player_x`, `enemy_list`, `init_game`).
- Priority Level: Low