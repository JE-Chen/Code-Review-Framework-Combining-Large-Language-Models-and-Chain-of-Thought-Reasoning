---

### Code Smell Type: Global State Usage  
**Problem Location:** All top-level variables (`screen`, `playerX`, `playerY`, `vx`, `vy`, `enemyList`, `scoreValue`, `runningGame`)  

**Detailed Explanation:**  
The entire game logic depends on global state, which reduces modularity and makes testing difficult. It also introduces side effects that can lead to hard-to-debug behavior when multiple functions interact with shared mutable state.

**Improvement Suggestions:**  
Refactor into a class-based structure where each variable is encapsulated within an object instance. This improves encapsulation, testability, and readability by making dependencies explicit.

**Priority Level:** High  

---

### Code Smell Type: Magic Numbers  
**Problem Location:**  
- `9` in `for i in range(9):`  
- `640`, `480`, `30`, `25`, `5` (WIDTH, HEIGHT, PLAYER_SIZE, ENEMY_SIZE, SPEED)  
- `27` in `clock.tick(27)`  

**Detailed Explanation:**  
Hardcoded values reduce flexibility and readability. These numbers should either be constants defined with descriptive names or configurable parameters for easier modification and reuse.

**Improvement Suggestions:**  
Replace hardcoded values with named constants or configuration objects. For example, replace `range(9)` with `ENEMY_COUNT = 9`.

**Priority Level:** Medium  

---

### Code Smell Type: Long Function  
**Problem Location:** `movePlayer()`  

**Detailed Explanation:**  
This function contains too much logic in one place. It handles both input detection and movement updates without clear separation of concerns. This makes it harder to understand and modify.

**Improvement Suggestions:**  
Split the function into smaller ones like `handleInput()`, `updatePosition()`, and `clampPosition()`. Each should have a single responsibility.

**Priority Level:** Medium  

---

### Code Smell Type: Tight Coupling  
**Problem Location:** `drawEverything()` uses direct access to `enemyList` and global `playerX`, `playerY`  

**Detailed Explanation:**  
Functions directly rely on external global state rather than accepting inputs or returning outputs. This creates tight coupling between components and limits reusability.

**Improvement Suggestions:**  
Pass necessary data as arguments instead of accessing globals directly. E.g., pass `player_pos`, `enemies`, and `score` to drawing functions.

**Priority Level:** High  

---

### Code Smell Type: Inconsistent Naming Conventions  
**Problem Location:** Mixed naming styles (`playerX`, `enemyList`, `scoreValue`, `WIDTH`, `HEIGHT`)  

**Detailed Explanation:**  
Variable names do not follow consistent casing rules (snake_case vs camelCase). This inconsistency hampers code comprehension and violates typical Python naming standards.

**Improvement Suggestions:**  
Use snake_case for all variables (`player_x`, `enemy_list`, etc.) per PEP 8 guidelines.

**Priority Level:** Medium  

---

### Code Smell Type: Violation of Single Responsibility Principle  
**Problem Location:** `checkCollision()` mixes collision detection with score update and respawn logic  

**Detailed Explanation:**  
One function performs multiple tasks—detecting collisions, updating scores, respawning enemies. This makes it hard to reason about and test in isolation.

**Improvement Suggestions:**  
Break down the function into subfunctions such as `detectCollisions()`, `updateScore()`, and `respawnEnemy()`.

**Priority Level:** High  

---

### Code Smell Type: Lack of Input Validation  
**Problem Location:** No checks for invalid positions or edge cases in movement or spawning  

**Detailed Explanation:**  
There's no validation against negative coordinates or out-of-bounds scenarios during initialization or runtime, which could lead to unexpected crashes or visual glitches.

**Improvement Suggestions:**  
Add bounds checking before setting positions and validate that enemy lists aren’t corrupted or empty.

**Priority Level:** Medium  

---

### Code Smell Type: Poor Exception Handling  
**Problem Location:** No error handling around Pygame calls or system exits  

**Detailed Explanation:**  
If Pygame fails to initialize or display fails, the application will crash silently. There’s no graceful degradation or informative logging.

**Improvement Suggestions:**  
Wrap critical sections in try-except blocks and log errors appropriately. At minimum, handle exceptions from `pygame.init()` and `pygame.quit()`.

**Priority Level:** Medium  

---

### Code Smell Type: Unused Imports  
**Problem Location:** `sys` imported but never used  

**Detailed Explanation:**  
Imported modules that are unused increase clutter and suggest poor maintenance practices.

**Improvement Suggestions:**  
Remove unused imports like `import sys`.

**Priority Level:** Low  

---

### Code Smell Type: Hardcoded Font Size  
**Problem Location:** `"Score: "` string concatenation and `font.render(...)` call  

**Detailed Explanation:**  
Using fixed-size fonts and manual rendering increases brittleness. If layout changes, rendering may break unexpectedly.

**Improvement Suggestions:**  
Define font sizes and rendering logic more dynamically or use a UI framework/library that supports layout management.

**Priority Level:** Medium  

---