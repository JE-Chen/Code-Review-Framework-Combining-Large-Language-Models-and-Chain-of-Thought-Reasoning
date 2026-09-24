### Code Review

#### 1. Readability & Consistency
- **Formatting:** The code is generally well-formatted and follows PEP 8 indentation.
- **Consistency:** The use of a global `STATE` dictionary is consistent, though it deviates from standard object-oriented patterns common in Pygame development.

#### 2. Naming Conventions
- **Function Names:** `do_everything()` and `draw_stuff()` are non-descriptive. They should be renamed to reflect their actual purpose (e.g., `update_game_state()` and `render_frame()`).
- **Variable Names:** `STATE` is used as a global variable; typically, constants are uppercase and mutable state is lowercase.

#### 3. Software Engineering Standards
- **Modularity:** The code lacks a main entry point. The game loop is executed at the top level of the script. It should be wrapped in a `def main():` function and called via `if __name__ == "__main__":`.
- **State Management:** Using a global dictionary for game state makes the code harder to test and scale. Consider using a `Game` class to encapsulate state and logic.
- **Resource Management:** `pygame.font.SysFont(None, 24)` is called inside `draw_stuff()`. This creates a new font object every single frame (57 times per second), which is a significant waste of resources. The font should be initialized once outside the loop.

#### 4. Logic & Correctness
- **Over-complicated Math:** In `move_player`, `int(math.sqrt(STATE["velocity"] ** 2))` is functionally equivalent to `abs(STATE["velocity"])`. This adds unnecessary complexity.
- **Inconsistent Movement:** The movement logic for `K_RIGHT` and `K_UP` uses absolute values, while `K_LEFT` and `K_DOWN` use the raw `STATE["velocity"]`. If `velocity` becomes negative, the player will move in opposite directions of the intended keys.
- **Logic Flaw:** `STATE["velocity"] or 1` in the `K_DOWN` block is a "magic" fallback that triggers only if velocity is exactly 0, creating inconsistent behavior compared to other directions.

#### 5. Performance & Security
- **Performance:** As mentioned in section 3, the font instantiation inside the render loop is a performance bottleneck.
- **Performance:** `time.time()` is used for delta calculation, but `pygame.time.Clock().tick()` already returns the delta time in milliseconds, which is the standard way to handle frame-independent movement in Pygame.

#### 6. Documentation & Testing
- **Documentation:** There are no docstrings or comments explaining the game logic or the purpose of the `STATE` variables.
- **Testing:** No unit tests are provided for the movement or state update logic.

---

### Summary of Recommendations
1. **Refactor** the game loop into a `main()` function and the state into a class.
2. **Move** font initialization outside the `draw_stuff` function.
3. **Simplify** the movement logic to remove redundant math (`sqrt` of a square) and ensure consistent directionality regardless of the sign of `velocity`.
4. **Rename** `do_everything` and `draw_stuff` to more professional, descriptive names.