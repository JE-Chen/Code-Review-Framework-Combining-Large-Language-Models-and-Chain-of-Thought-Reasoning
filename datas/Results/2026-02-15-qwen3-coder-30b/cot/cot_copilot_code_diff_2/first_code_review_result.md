### Code Review Summary

#### 1. **Readability & Consistency**
- Indentation and structure are mostly consistent but can benefit from spacing around operators and after control flow statements for better visual separation.
- Comments are missing; adding brief inline comments would help clarify intent.

#### 2. **Naming Conventions**
- Global variables like `playerX`, `enemyList`, etc., use vague names. Consider more descriptive alternatives (e.g., `player_x`, `enemies`).
- Function names (`movePlayer`, `checkCollision`) are clear, but could include units or types where applicable.

#### 3. **Software Engineering Standards**
- Heavy use of global state makes testing and modularity difficult. Encapsulate game state into classes.
- Repeated logic (e.g., boundary checks) should be abstracted into helper functions.
- No clear separation between game logic and rendering — consider separating concerns.

#### 4. **Logic & Correctness**
- Collision detection works, but does not account for moving enemies or precise pixel-level interactions.
- Player movement uses velocity but doesn’t handle acceleration/deceleration smoothly.
- Score increases even when collisions occur outside visible area due to lack of frame synchronization.

#### 5. **Performance & Security**
- No major performance issues detected, but inefficient drawing of all elements every frame may become problematic as complexity grows.
- No explicit input validation or sanitization needed here, though proper bounds checking is assumed.

#### 6. **Documentation & Testing**
- Missing docstrings and inline comments. Add basic documentation for each function.
- No unit tests provided. Suggest mocking core components (e.g., `pygame`) for easier testing.

#### 7. **Suggestions for Improvement**
- Replace globals with a class-based structure for encapsulation.
- Extract repeated logic into helper functions (e.g., boundary checks).
- Improve naming consistency (`playerX` → `player_x`).
- Add minimal comments explaining key behaviors.
- Refactor collision logic to support dynamic updates without side effects.

Overall, the code is functional but requires structural improvements for scalability and maintainability.