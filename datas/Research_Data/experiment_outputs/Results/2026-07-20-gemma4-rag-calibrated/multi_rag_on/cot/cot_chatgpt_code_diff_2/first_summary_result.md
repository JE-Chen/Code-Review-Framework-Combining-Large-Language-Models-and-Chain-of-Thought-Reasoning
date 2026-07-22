### PR Summary

*   **Key changes**: Implemented a basic game loop using `pygame` featuring a movable player circle, a dynamic scoring system, and color-shifting backgrounds.
*   **Impact scope**: New file `game.py`.
*   **Purpose of changes**: Initial implementation of game mechanics and rendering.
*   **Items to confirm**: Review the use of global state and the logic within the movement and update functions.

---

### Code Review

#### 1. Readability & Consistency
*   **Naming**: The function name `do_everything` is too generic and does not describe its purpose (which seems to be updating game state and handling specific events). It should be renamed to something like `update_game_state`.

#### 2. Software Engineering Standards
*   **Modularity**: The code relies heavily on a global `STATE` dictionary. This creates tight coupling and makes the code difficult to test or extend.
*   **Recommendation**: Encapsulate the game state into a `Game` class or a dedicated state object and pass it as an argument to functions.

#### 3. Logic & Correctness
*   **Redundant Logic**: In `move_player`, the line `STATE["player"][0] += int(math.sqrt(STATE["velocity"] ** 2))` is a mathematically complex way of writing `abs(STATE["velocity"])`.
*   **Inconsistent Movement**: The movement logic uses `STATE["velocity"]` for some directions and `abs()` or `or 1` for others. This results in inconsistent behavior if `velocity` becomes negative or zero.

#### 4. Performance & Security
*   **Resource Management**: `pygame.font.SysFont(None, 24)` is called inside `draw_stuff()`, which runs every frame (approx. 57 times per second). Creating a font object every frame is a significant performance bottleneck.
*   **Recommendation**: Initialize the font once outside the main loop and reuse the object.

#### 5. RAG Rules Violations
*   **Shared Mutable State**: The use of the global `STATE` dictionary is a direct violation of the rule: *"Be careful with shared mutable state at the module or class level... Prefer passing state explicitly."*
*   **Magic Numbers**: There are several hard-coded constants (e.g., `10`, `15`, `57`, `255`, `24`) scattered throughout the logic. These should be defined as named constants at the top of the file (e.g., `FPS = 57`, `PLAYER_RADIUS_BASE = 10`).
*   **Testability**: Because the logic is tied to global state and direct `pygame` calls, it is nearly impossible to unit test the movement or scoring logic without initializing a full display window.

### Summary of Suggested Changes
1.  **Refactor `STATE`** into a class to remove global mutable state.
2.  **Move `SysFont` initialization** outside the `draw_stuff` function.
3.  **Simplify movement math** (remove `sqrt` and `** 2`).
4.  **Replace magic numbers** with descriptive constants.
5.  **Rename `do_everything`** to reflect its actual purpose.