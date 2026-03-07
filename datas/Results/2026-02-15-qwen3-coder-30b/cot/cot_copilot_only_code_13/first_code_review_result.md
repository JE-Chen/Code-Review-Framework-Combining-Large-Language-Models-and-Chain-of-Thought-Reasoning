### Code Review Summary

#### 1. **Readability & Consistency**
- Indentation is consistent but could benefit from spacing around operators for clarity.
- Comments are minimal; consider adding brief inline comments to explain key logic steps.

#### 2. **Naming Conventions**
- Variables like `playerX`, `playerY` are descriptive, but global state usage makes them harder to manage.
- Function names (`movePlayer`, `checkCollision`) are clear, but lack context about what they do beyond their name.

#### 3. **Software Engineering Standards**
- Heavy use of global variables leads to tight coupling and reduces modularity.
- No encapsulation or class-based design; hard to extend or test independently.

#### 4. **Logic & Correctness**
- Collision detection works but may miss edge cases due to integer comparisons.
- Player bounds enforcement is correct but can be simplified using `max()`/`min()`.

#### 5. **Performance & Security**
- No major performance issues; game loop runs at fixed FPS.
- No user input sanitization needed here since it's a simple local game.

#### 6. **Documentation & Testing**
- Minimal inline documentation.
- No unit tests provided — difficult to verify behavior without manual testing.

---

### Suggestions for Improvement

- Replace globals with parameters or classes for better structure and testability.
- Simplify boundary checks using helper functions.
- Add docstrings or comments to clarify core game mechanics.
- Refactor collision logic into reusable components if expanding later.