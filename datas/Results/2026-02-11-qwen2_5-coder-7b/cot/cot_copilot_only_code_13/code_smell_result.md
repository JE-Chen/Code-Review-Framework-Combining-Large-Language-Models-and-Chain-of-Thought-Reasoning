### Code Smell Analysis

#### 1. Long Function
- **Code Smell Type**: Long Function
- **Problem Location**: `movePlayer` function
- **Detailed Explanation**: The `movePlayer` function contains multiple conditional checks and logic to handle player movement and boundaries. This makes the function difficult to read and understand.
- **Improvement Suggestions**: Break down the function into smaller functions, each responsible for a specific task (e.g., checking key presses, updating position, applying boundaries).
- **Priority Level**: High

#### 2. Magic Numbers
- **Code Smell Type**: Magic Numbers
- **Problem Location**: Multiple places throughout the code (e.g., `WIDTH`, `HEIGHT`, `PLAYER_SIZE`, `ENEMY_SIZE`, `SPEED`)
- **Detailed Explanation**: Hardcoded values make the code less flexible and harder to maintain. They also reduce readability.
- **Improvement Suggestions**: Define these constants at the top of the file or use configuration files if applicable.
- **Priority Level**: Medium

#### 3. Global Variables
- **Code Smell Type**: Global Variables
- **Problem Location**: Many variables (`screen`, `playerX`, `playerY`, `vx`, `vy`, `enemyList`, `scoreValue`, `runningGame`) are declared globally.
- **Detailed Explanation**: Global state can lead to unexpected side effects and make the code harder to reason about.
- **Improvement Suggestions**: Pass required parameters through function arguments or encapsulate them within classes.
- **Priority Level**: High

#### 4. Lack of Abstraction
- **Code Smell Type**: Lack of Abstraction
- **Problem Location**: Functions like `initGame`, `drawEverything`, `checkCollision`, and `mainLoop` do not clearly define their responsibilities.
- **Detailed Explanation**: The lack of clear abstractions makes the code hard to understand and extend.
- **Improvement Suggestions**: Refactor functions to have a single responsibility and extract common functionality into helper methods.
- **Priority Level**: Medium

#### 5. Unnecessary Complexity
- **Code Smell Type**: Unnecessary Complexity
- **Problem Location**: The game loop in `mainLoop` has redundant calls to `clock.tick(30)`.
- **Detailed Explanation**: Redundant calls to `clock.tick` do not provide any additional value and can be simplified.
- **Improvement Suggestions**: Remove redundant calls.
- **Priority Level**: Low

#### 6. Inadequate Comments
- **Code Smell Type**: Inadequate Comments
- **Problem Location**: Most functions lack comments explaining their purpose.
- **Detailed Explanation**: Lack of comments reduces the readability and maintainability of the code.
- **Improvement Suggestions**: Add Javadoc-style comments above each function explaining its purpose and parameters.
- **Priority Level**: Medium

### Summary

The provided code exhibits several code smells that impact its readability, maintainability, and scalability. Addressing these issues will improve the overall quality of the codebase.