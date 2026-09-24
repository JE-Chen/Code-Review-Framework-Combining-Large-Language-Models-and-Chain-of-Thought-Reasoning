### Code Review

#### 1. Readability & Consistency
- **Formatting:** The code generally follows PEP 8; however, the logic within `move_player` and `do_everything` is inconsistent and lacks clarity.
- **Comments:** There are no comments explaining the purpose of the "game" logic or the specific behavior of the state updates.

#### 2. Naming Conventions
- **Function Naming:** `do_everything()` is a poor name. It violates the principle of descriptive naming as it handles event processing, time tracking, score updates, and color shifts simultaneously. It should be split into specific functions (e.g., `update_game_state`, `handle_input`).
- **Variable Naming:** `STATE` is used as a global dictionary. While descriptive of its role, using a class or a named tuple would provide better structure and type safety.

#### 3. Software Engineering Standards
- **Modularity:** The code lacks a proper entry point (e.g., `if __name__ == "__main__":`).
- **Global State:** The reliance on a global `STATE` dictionary makes the code difficult to test and maintain.
- **Resource Management:** The `pygame.font.SysFont` is called inside `draw_stuff()`, which runs every frame. This is highly inefficient; the font should be initialized once outside the main loop.

#### 4. Logic & Correctness
- **Redundant Logic:** In `move_player`, `int(math.sqrt(STATE["velocity"] ** 2))` is a computationally expensive way to write `abs(STATE["velocity"])`.
- **Inconsistent Movement:** 
    - `K_LEFT` uses `STATE["velocity"]`.
    - `K_RIGHT` uses the absolute value.
    - `K_UP` uses the absolute value.
    - `K_DOWN` uses `STATE["velocity"] or 1`.
    If `velocity` becomes negative, the player will move in opposite directions to the keys pressed.
- **Score Logic:** `STATE["score"] += int(delta * 10) % 7` results in a very erratic score increase that doesn't correlate to any gameplay achievement.

#### 5. Performance & Security
- **Performance:** As mentioned, creating a `font` object every frame in `draw_stuff()` will cause significant performance degradation and memory churn over time.
- **Frame Rate:** `clock.tick(57)` is an unusual choice; typically, 60 FPS is the standard for smooth movement.

#### 6. Documentation & Testing
- **Documentation:** There is no documentation or README explaining how to run the code or what the intended gameplay is.
- **Testing:** No unit tests are provided for the movement or state logic.

---

### Summary of Recommendations
1. **Refactor `do_everything`**: Split into `handle_events` and `update_state`.
2. **Optimize Rendering**: Move `pygame.font.SysFont` outside the main loop.
3. **Simplify Math**: Replace `math.sqrt(...)` with `abs()`.
4. **Standardize Movement**: Ensure `velocity` is handled consistently across all four directions.
5. **Encapsulate State**: Move the `STATE` dictionary into a `Game` class.