### Code Smell Type: Global Variable Usage
- **Problem Location:** Lines 6–12 (`playerX`, `playerY`, `vx`, `vy`, `enemyList`, `scoreValue`, `runningGame`)
- **Detailed Explanation:** The use of global variables throughout the code makes the code hard to test, debug, and maintain. It creates tight coupling between functions and reduces modularity. Changes to these variables can have unintended side effects across different parts of the application.
- **Improvement Suggestions:** Encapsulate game state into a class (e.g., `Game`) to manage all game-related data and behavior. This improves encapsulation and allows for easier testing and reuse.
- **Priority Level:** High

---

### Code Smell Type: Magic Numbers
- **Problem Location:** Line 16 (`for i in range(9):`)
- **Detailed Explanation:** Using hardcoded values like `9` for the number of enemies reduces readability and flexibility. If you ever want to change the number of enemies, you must manually update this value in multiple places.
- **Improvement Suggestions:** Replace the magic number with a named constant such as `NUM_ENEMIES = 9`. This makes intent clearer and simplifies future modifications.
- **Priority Level:** Medium

---

### Code Smell Type: Long Function
- **Problem Location:** Function `movePlayer()` (lines 21–33)
- **Detailed Explanation:** The `movePlayer` function performs both input handling and movement logic, violating the Single Responsibility Principle (SRP). Additionally, it contains repetitive conditional checks and direct state updates, which could be simplified and made more readable.
- **Improvement Suggestions:** Split this function into smaller ones: one for handling key presses, another for updating position based on velocity. Also, consider using vector math for cleaner movement logic.
- **Priority Level:** High

---

### Code Smell Type: Poor Naming Conventions
- **Problem Location:** Variables `vx`, `vy` (line 8); `playerX`, `playerY` (line 7)
- **Detailed Explanation:** While these variable names are somewhat descriptive, they don't clearly indicate their role within the context of movement or velocity. A better naming convention would make the code more self-documenting.
- **Improvement Suggestions:** Rename `vx`, `vy` to `velocity_x`, `velocity_y` and `playerX`, `playerY` to `player_pos_x`, `player_pos_y`. This enhances clarity and aligns with common Python naming standards.
- **Priority Level:** Medium

---

### Code Smell Type: Lack of Abstraction
- **Problem Location:** In `checkCollision()` and `drawEverything()`
- **Detailed Explanation:** The collision detection logic and drawing logic are tightly coupled to the current implementation and lack abstraction. For example, enemy positions are accessed directly via list indices (`e[0]`, `e[1]`) instead of being abstracted through a proper object-oriented approach.
- **Improvement Suggestions:** Define classes like `Player` and `Enemy` with properties such as `x`, `y`, `width`, `height`. Then, implement methods like `collides_with(other)` and `draw(surface)`. This promotes reusability and maintainability.
- **Priority Level:** High

---

### Code Smell Type: Inconsistent Indentation and Formatting
- **Problem Location:** General formatting inconsistencies in some lines
- **Detailed Explanation:** Although minimal, there are slight variations in spacing and indentation that deviate from standard PEP 8 guidelines. These small issues can reduce readability when working in teams or larger codebases.
- **Improvement Suggestions:** Run a linter like `flake8` or `black` to enforce consistent formatting and indentation. Ensure all lines are indented uniformly with spaces (typically 4 spaces per level).
- **Priority Level:** Low

---

### Code Smell Type: Hardcoded Constants
- **Problem Location:** Lines 17–20 (`WIDTH`, `HEIGHT`, `PLAYER_SIZE`, `ENEMY_SIZE`, `SPEED`)
- **Detailed Explanation:** Though constants are used, they're still hardcoded at the top level without any structure. If you need to configure them dynamically or load them from external sources (like config files), this approach won't scale well.
- **Improvement Suggestions:** Consider loading these values from a configuration file or passing them as parameters during initialization. Alternatively, define them inside a class or module-level dictionary for better organization.
- **Priority Level:** Medium

---

### Code Smell Type: Tight Coupling Between Functions
- **Problem Location:** All major functions (`initGame`, `movePlayer`, `drawEverything`, `checkCollision`, `mainLoop`) interact with global variables
- **Detailed Explanation:** Each function depends on shared mutable global state, making it difficult to isolate components for testing or reuse. This leads to fragile dependencies and increases complexity.
- **Improvement Suggestions:** Refactor so that each function operates on explicit inputs and returns outputs rather than relying on global state. Pass necessary objects (like player, enemies) to functions explicitly.
- **Priority Level:** High

---

### Code Smell Type: Duplicate Logic
- **Problem Location:** Boundary checking in `movePlayer()` (lines 29–32)
- **Detailed Explanation:** The repeated boundary checks for `playerX` and `playerY` are redundant and can be consolidated into a helper function to improve maintainability and reduce duplication.
- **Improvement Suggestions:** Create a utility function like `clamp_position(pos_x, pos_y, width, height, size)` to handle boundary constraints cleanly.
- **Priority Level:** Medium

---

### Code Smell Type: No Input Validation or Error Handling
- **Problem Location:** Entire script lacks error handling or input validation
- **Detailed Explanation:** There’s no protection against invalid inputs or runtime exceptions, especially concerning `pygame` operations. If `pygame` fails to initialize or a window isn't created correctly, the program will crash silently or behave unpredictably.
- **Improvement Suggestions:** Add try-except blocks around critical sections (e.g., `pygame.init()`). Validate screen dimensions and other assumptions before proceeding.
- **Priority Level:** Medium

---

### Code Smell Type: Use of Magic Strings
- **Problem Location:** Line 38 (`"Score: " + str(scoreValue)`)
- **Detailed Explanation:** Hardcoded strings like `"Score: "` reduce flexibility and make localization harder. It also doesn’t follow DRY principles if similar messages appear elsewhere.
- **Improvement Suggestions:** Move string literals into constants or use a translation system if internationalization is needed. Example: `SCORE_TEXT = "Score: "`.
- **Priority Level:** Medium

---

### Summary Table

| Code Smell Type                  | Priority Level |
|----------------------------------|----------------|
| Global Variable Usage            | High           |
| Magic Numbers                    | Medium         |
| Long Function                    | High           |
| Poor Naming Conventions          | Medium         |
| Lack of Abstraction              | High           |
| Inconsistent Indentation         | Low            |
| Hardcoded Constants              | Medium         |
| Tight Coupling Between Functions | High           |
| Duplicate Logic                  | Medium         |
| No Input Validation              | Medium         |
| Use of Magic Strings             | Medium         |

This analysis highlights areas where structural improvements can significantly enhance code quality, readability, and maintainability.