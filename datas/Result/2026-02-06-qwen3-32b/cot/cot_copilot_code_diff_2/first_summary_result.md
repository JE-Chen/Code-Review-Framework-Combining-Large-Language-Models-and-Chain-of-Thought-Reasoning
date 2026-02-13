### Code Review: game.py

#### ✅ Readability & Consistency
- **Positive**: Consistent 4-space indentation, clear function separation, and logical flow.
- **Improvement**: Heavy use of global variables (`playerX`, `enemyList`, `scoreValue`) reduces readability. Replace with class-based state management for encapsulation.

#### ✅ Naming Conventions
- **Clear**: `initGame`, `movePlayer`, `checkCollision` are descriptive.
- **Ambiguous**: `vx`, `vy` lack context. Rename to `player_velocity_x`, `player_velocity_y` for clarity.
- **Inconsistent**: `enemyList` (snake_case) vs. `WIDTH`/`HEIGHT` (UPPER_SNAKE). Standardize to `ENEMY_LIST` or use class properties.

#### ⚠️ Software Engineering
- **Critical Issue**: Global state makes code untestable and error-prone. Example: `checkCollision` directly mutates `enemyList` without validation.
- **Refactoring Needed**: Encapsulate game state in a `Game` class with methods like `handle_input()`, `update()`, and `render()`. This enables unit testing and reduces side effects.

#### ✅ Logic & Correctness
- **Correct**: AABB collision detection and boundary checks are implemented properly.
- **Edge Case**: If player collides with multiple enemies in one frame, all are reset. This is acceptable but should be documented.

#### ✅ Performance & Security
- **No Issues**: Fixed enemy count (9) and simple collision checks are efficient. No security risks.

#### ❌ Documentation & Testing
- **Missing**: Zero comments explaining core logic (e.g., collision math).
- **Critical Gap**: No unit tests for `checkCollision` or boundary handling. Add tests for:
  ```python
  def test_collision():
      # Mock player/enemy positions and verify score increment
  ```

---

### Key Recommendations
1. **Replace globals with a `Game` class**:
   ```python
   class Game:
       def __init__(self):
           self.player_x = 100
           self.player_y = 100
           self.enemies = [...]  # Initialize enemies
   ```
2. **Rename `vx`/`vy`** to `player_velocity_x`/`player_velocity_y`.
3. **Add docstrings** for all functions (e.g., `checkCollision` explains collision behavior).
4. **Write unit tests** for collision logic and boundary conditions.

---

### Impact Summary
| Category          | Status       | Details                                                                 |
|-------------------|--------------|-------------------------------------------------------------------------|
| **Readability**   | ⚠️ Needs Fix | Globals hinder clarity; class-based structure required.                   |
| **Testability**   | ❌ Critical  | No tests; refactoring to OOP enables unit testing.                        |
| **Correctness**   | ✅ Valid     | Logic correct but edge cases untested.                                  |
| **Maintainability**| ⚠️ Low       | Global state increases risk of bugs in future changes.                    |

---

### Items to Confirm
1. Is the `enemyList` mutation in `checkCollision` intentional? (Should be safe for small scale.)
2. Will the `Game` class refactor break existing dependencies? (Minimal impact since this is a new module.)
3. Are tests being added for collision and boundary logic? (Critical for stability.)

> **Final Note**: The code works for a simple game, but the global state violates core engineering principles. Refactoring to OOP will significantly improve quality without major effort. Prioritize this before adding features.