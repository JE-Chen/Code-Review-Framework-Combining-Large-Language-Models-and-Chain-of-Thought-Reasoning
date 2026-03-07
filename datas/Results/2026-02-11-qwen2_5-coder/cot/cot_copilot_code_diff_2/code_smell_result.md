## Code Smell Type: Global Variables
- **Problem Location:** `playerX`, `playerY`, `vx`, `vy`, `enemyList`, `scoreValue`, `runningGame`, `WIDTH`, `HEIGHT`, `PLAYER_SIZE`, `ENEMY_SIZE`, `SPEED`
- **Detailed Explanation:** The use of global variables can lead to tightly coupled code, making it harder to understand, test, and modify. It also increases the risk of unintended side effects when variables are modified from different parts of the application.
- **Improvement Suggestions:** Encapsulate these variables within classes or functions to limit their scope and expose only the necessary parts through methods or properties.
- **Priority Level:** High

## Code Smell Type: Magic Numbers
- **Problem Location:** `SPEED` (used multiple times), `WIDTH`, `HEIGHT`, `PLAYER_SIZE`, `ENEMY_SIZE`
- **Detailed Explanation:** Magic numbers make the code less readable and harder to maintain. They are hard-coded values without clear meaning.
- **Improvement Suggestions:** Define constants at the top of the file or encapsulate them within a configuration object.
- **Priority Level:** Medium

## Code Smell Type: Long Method
- **Problem Location:** `mainLoop`
- **Detailed Explanation:** The `mainLoop` method contains too much functionality, leading to a complex and difficult-to-test piece of code.
- **Improvement Suggestions:** Break down the `mainLoop` into smaller methods, each responsible for a single aspect of the game loop (event handling, updating, drawing).
- **Priority Level:** Medium

## Code Smell Type: Lack of Abstraction
- **Problem Location:** No classes or functions abstracting game entities (player, enemies).
- **Detailed Explanation:** The code lacks abstractions, making it harder to manage complexity and extend the game's features.
- **Improvement Suggestions:** Create classes for game entities (Player, Enemy) and encapsulate their behavior and state within these classes.
- **Priority Level:** Medium

## Code Smell Type: Unnecessary Complexity
- **Problem Location:** Complex collision detection logic within `checkCollision`.
- **Detailed Explanation:** The collision detection could be simplified using geometric principles.
- **Improvement Suggestions:** Simplify the collision detection algorithm or use built-in libraries where appropriate.
- **Priority Level:** Low

## Code Smell Type: Lack of Comments
- **Problem Location:** Most of the code lacks comments explaining its purpose.
- **Detailed Explanation:** Without comments, other developers will have difficulty understanding the code's intent.
- **Improvement Suggestions:** Add comments above key functions and blocks of code to explain their purpose and how they contribute to the overall functionality.
- **Priority Level:** Medium

## Code Smell Type: Missing Error Handling
- **Problem Location:** No error handling around external dependencies like `pygame.init()`.
- **Detailed Explanation:** Missing error handling can lead to runtime exceptions and crashes.
- **Improvement Suggestions:** Implement try-except blocks around critical operations to handle potential errors gracefully.
- **Priority Level:** Medium

## Code Smell Type: Hardcoded Exit Condition
- **Problem Location:** `endGame()` called directly from `mainLoop`.
- **Detailed Explanation:** Directly calling exit functions can hide the termination path and make debugging difficult.
- **Improvement Suggestions:** Use a more controlled way to terminate the game loop and ensure proper cleanup.
- **Priority Level:** Low