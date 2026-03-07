---

### Code Smell Type: Global State Dependency
- **Problem Location**: `initGame`, `movePlayer`, `drawEverything`, `checkCollision`, and `mainLoop` functions all access and mutate global variables (`screen`, `playerX`, `playerY`, `vx`, `vy`, `enemyList`, `scoreValue`, `runningGame`)
- **Detailed Explanation**: The use of global state makes the code tightly coupled and hard to reason about. It reduces modularity, makes testing difficult, and increases the chance of unintended side effects. Each function relies on external state rather than explicit parameters or return values.
- **Improvement Suggestions**: Refactor the game into classes with encapsulated state (e.g., `Game` class). Pass necessary data through constructor or method arguments instead of relying on globals.
- **Priority Level**: High

---

### Code Smell Type: Magic Numbers
- **Problem Location**: Hardcoded constants like `WIDTH=640`, `HEIGHT=480`, `PLAYER_SIZE=30`, `ENEMY_SIZE=25`, `SPEED=5`
- **Detailed Explanation**: These numeric literals make the code less readable and harder to update. If any dimension changes, you must manually find and replace all occurrences. This also hinders future extensions.
- **Improvement Suggestions**: Define named constants at module level or in a configuration file/class to improve clarity and maintainability.
- **Priority Level**: Medium

---

### Code Smell Type: Long Function
- **Problem Location**: `movePlayer()` and `checkCollision()`
- **Detailed Explanation**: `movePlayer()` performs multiple actions without clear separation of concerns. Similarly, `checkCollision()` combines movement logic and collision detection. Both violate the Single Responsibility Principle.
- **Improvement Suggestions**: Break down these functions into smaller, focused ones such as `updateVelocity()`, `applyMovement()`, `detectCollisions()`, etc.
- **Priority Level**: High

---

### Code Smell Type: Duplicated Logic
- **Problem Location**: Boundary checks in `movePlayer()` (`if playerX < 0: playerX = 0`)
- **Detailed Explanation**: Repetition of boundary condition checks increases redundancy and makes future modifications error-prone.
- **Improvement Suggestions**: Extract boundary checking into a helper function or integrate it within a physics engine abstraction.
- **Priority Level**: Medium

---

### Code Smell Type: Tight Coupling Between Components
- **Problem Location**: `drawEverything()` directly accesses global `screen` and `enemyList`
- **Detailed Explanation**: The rendering logic is tightly coupled with game state, making it difficult to swap rendering engines or test independently.
- **Improvement Suggestions**: Introduce an interface or abstraction layer between drawing logic and core game components.
- **Priority Level**: Medium

---

### Code Smell Type: Inconsistent Naming Conventions
- **Problem Location**: Mixed case styles (`playerX`, `playerY`, `enemyList`, `scoreValue`) and abbreviations (`vx`, `vy`)
- **Detailed Explanation**: While not incorrect per se, inconsistent naming reduces readability and can confuse new developers unfamiliar with the project.
- **Improvement Suggestions**: Adopt snake_case convention consistently throughout the codebase.
- **Priority Level**: Low

---

### Code Smell Type: Lack of Input Validation
- **Problem Location**: No validation of inputs passed to game loop or state updates
- **Detailed Explanation**: There’s no protection against invalid states or edge cases, which could lead to runtime errors or unexpected behavior.
- **Improvement Suggestions**: Add checks for valid ranges and types where applicable.
- **Priority Level**: Medium

---

### Code Smell Type: Poor Separation of Concerns
- **Problem Location**: Mixing UI logic (`drawEverything`), game mechanics (`movePlayer`, `checkCollision`), and control flow (`mainLoop`)
- **Detailed Explanation**: This violates the principle of separation of concerns and results in monolithic functions that are hard to debug and extend.
- **Improvement Suggestions**: Separate concerns into dedicated modules: input handler, game logic manager, renderer, and main application loop.
- **Priority Level**: High

---

### Code Smell Type: Hardcoded Font Size and Position
- **Problem Location**: `font = pygame.font.SysFont(None, 36)` and positioning `(10, 10)`
- **Detailed Explanation**: Hardcoding font sizes and positions reduces flexibility and makes UI adjustments cumbersome.
- **Improvement Suggestions**: Make layout configurable via settings or constants.
- **Priority Level**: Low

---

### Code Smell Type: Unused Imports or Variables
- **Problem Location**: `import sys` — never used
- **Detailed Explanation**: Unused imports clutter the namespace and suggest incomplete cleanup.
- **Improvement Suggestions**: Remove unused imports.
- **Priority Level**: Low

---

### Summary Table

| Code Smell Type              | Priority |
|-----------------------------|----------|
| Global State Dependency     | High     |
| Magic Numbers               | Medium   |
| Long Function               | High     |
| Duplicated Logic            | Medium   |
| Tight Coupling              | Medium   |
| Inconsistent Naming         | Low      |
| Lack of Input Validation    | Medium   |
| Poor Separation of Concerns | High     |
| Hardcoded Font Size/Position| Low      |
| Unused Imports              | Low      |

--- 

This review identifies several areas for improvement focusing on design principles, maintainability, and extensibility. Prioritizing high-severity issues will significantly enhance the overall quality of the codebase.