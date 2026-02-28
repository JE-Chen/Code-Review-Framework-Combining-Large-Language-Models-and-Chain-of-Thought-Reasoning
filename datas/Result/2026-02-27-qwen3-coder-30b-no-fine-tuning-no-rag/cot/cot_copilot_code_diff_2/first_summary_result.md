## Pull Request Summary

### Key Changes
- Introduced a new Pygame-based game with player movement, enemy spawning, collision detection, and scoring.
- Implemented core game loop with keyboard input handling and rendering logic.

### Impact Scope
- Affects `game.py` only — a standalone game module.
- Uses standard Python libraries (`pygame`, `random`, `sys`) and global state management.

### Purpose of Changes
- Adds a functional prototype game to demonstrate basic Pygame concepts such as event handling, sprite movement, and collision detection.

### Risks and Considerations
- Heavy use of global variables may lead to maintainability issues in larger codebases.
- No error handling or input sanitization for edge cases (e.g., invalid screen dimensions).
- Game logic tightly coupled to `mainLoop()` which reduces testability.

### Items to Confirm
- Ensure `pygame` is properly installed and compatible with target environment.
- Consider refactoring globals into a class for better encapsulation and testability.
- Validate behavior under different window sizes or resolutions.

---

## Code Review

### 1. **Readability & Consistency**
- ✅ Indentation and structure are consistent and readable.
- ⚠️ Comments are missing; adding brief inline comments could improve understanding.
- ⚠️ Formatting uses standard Python conventions but lacks tooling enforcement (e.g., black, flake8).

### 2. **Naming Conventions**
- ⚠️ Global variables like `playerX`, `playerY`, `enemyList`, etc., are not descriptive enough.
- ❌ Inconsistent naming: `WIDTH`, `HEIGHT`, `SPEED` are uppercase (constants) but `vx`, `vy` are lowercase (variables).
- ✅ Function names (`initGame`, `movePlayer`) are clear and descriptive.

### 3. **Software Engineering Standards**
- ❌ Heavy reliance on global variables makes code hard to test and maintain.
- ❌ Duplicated logic in boundary checks can be abstracted into helper functions.
- ⚠️ The `mainLoop` function handles too many responsibilities (input, update, render).
- ✅ Modular structure exists, but could benefit from object-oriented design.

### 4. **Logic & Correctness**
- ✅ Collision detection logic appears correct for axis-aligned rectangles.
- ⚠️ Player position clamping works, but assumes fixed size — consider dynamic sizing.
- ⚠️ Enemies respawn at random positions without checking if they overlap with other enemies or player.

### 5. **Performance & Security**
- ⚠️ `clock.tick(27)` limits FPS to ~27, potentially causing responsiveness issues.
- ⚠️ No input validation or bounds checking for `WIDTH`, `HEIGHT`.
- ❌ Risk of infinite loop due to lack of early exit when game ends.

### 6. **Documentation & Testing**
- ❌ No docstrings or inline comments explaining purpose or parameters.
- ❌ No unit or integration tests provided — critical for verifying game behavior.

### 7. **Overall Recommendations**
- Refactor global state into a class for improved encapsulation and testability.
- Add docstrings and comments to explain key functions and behaviors.
- Implement unit tests for `checkCollision` and `movePlayer`.
- Use constants consistently with snake_case or UPPER_CASE naming.
- Consider modularizing game components (e.g., player, enemy classes) for scalability.

**Rating: ⚠️ Moderate Risk**

This is a working prototype but needs significant improvements before production use.