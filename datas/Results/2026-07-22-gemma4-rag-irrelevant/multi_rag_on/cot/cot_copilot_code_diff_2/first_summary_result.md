### Code Review

#### 1. Readability & Consistency
- **Formatting**: The code generally follows a consistent indentation pattern. However, some conditional statements are written on a single line (e.g., `if playerX < 0: playerX = 0`), which deviates from PEP 8 standards and reduces readability.
- **Consistency**: The use of `global` variables throughout the script makes the state management difficult to track and inconsistent with modern Python practices.

#### 2. Naming Conventions
- **Variable Naming**: The codebase uses a mix of `camelCase` (`playerX`, `enemyList`, `scoreValue`, `runningGame`) and `snake_case` (implied by `initGame` and `mainLoop` though they are functions). 
- **Recommendation**: Follow PEP 8 conventions:
    - Functions and variables should be `snake_case` (e.g., `player_x`, `enemy_list`, `init_game`).
    - Constants are correctly defined in `UPPER_CASE`.

#### 3. Software Engineering Standards
- **Modularity**: The code relies heavily on global state. This makes the logic hard to test in isolation and prevents the possibility of running multiple game instances or resetting the game state easily.
- **Abstraction**: 
    - The player and enemies are represented as raw coordinates/lists. Encapsulating these into classes (e.g., `Player` and `Enemy`) would improve maintainability and allow for easier expansion of properties (like color or speed).
    - The `drawEverything` function handles both logic (font creation) and rendering.

#### 4. Logic & Correctness
- **Resource Management**: `pygame.font.SysFont(None, 36)` is called inside `drawEverything`, which runs every frame (27 times per second). This is inefficient as it re-initializes the font object constantly.
- **Boundary Conditions**: Player boundary checks are correctly implemented to keep the player within the screen dimensions.

#### 5. Performance & Security
- **Performance**: As mentioned, moving the font initialization out of the main loop and into `initGame` would reduce CPU overhead.
- **Security**: No external inputs are processed, so there are no immediate security vulnerabilities.

#### 6. Documentation & Testing
- **Documentation**: The code lacks docstrings and comments explaining the purpose of the functions.
- **Testing**: There are no unit tests provided for the collision logic or movement constraints.

---

### Summary of Recommendations

| Category | Issue | Suggestion |
| :--- | :--- | :--- |
| **Architecture** | Heavy use of `global` variables | Wrap game state in a class or pass objects as arguments. |
| **Performance** | Font created every frame | Initialize the font once in `initGame`. |
| **Naming** | Inconsistent `camelCase` | Rename variables and functions to `snake_case` per PEP 8. |
| **Design** | Primitive data structures | Use classes for `Player` and `Enemy` entities. |
| **Style** | Single-line `if` statements | Expand to multiple lines for better clarity. |