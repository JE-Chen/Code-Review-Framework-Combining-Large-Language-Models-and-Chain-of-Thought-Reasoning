### Code Review

**1. Readability & Naming**
*   **Vague Naming:** `do_everything()` and `draw_stuff()` are non-descriptive. Rename them to reflect their actual purpose (e.g., `update_game_state()` and `render_frame()`).
*   **Magic Numbers:** The code contains several hard-coded values (e.g., `clock.tick(57)`, `delta * 10 % 7`, `10 + STATE["score"] % 15`). These should be defined as named constants at the top of the file.

**2. Software Engineering Standards**
*   **Shared Mutable State:** The use of a global `STATE` dictionary introduces hidden coupling. This makes the code difficult to test and scale. Encapsulate the game state into a class (e.g., `GameState`).
*   **Resource Management:** `pygame.font.SysFont(None, 24)` is called every single frame inside `draw_stuff()`. This is a significant performance bottleneck; the font should be initialized once outside the main loop.

**3. Logic & Correctness**
*   **Over-complicated Logic:** In `move_player`, `int(math.sqrt(STATE["velocity"] ** 2))` is a computationally expensive way to write `abs(STATE["velocity"])`.
*   **Unpredictable Movement:** `STATE["velocity"]` can become negative or zero due to `random.choice([-1, 0, 1])`. This causes the player to move in reverse or stop entirely, which may be unintended behavior.
*   **Redundant Logic:** `STATE["velocity"] or 1` in the `K_DOWN` block is inconsistent with how other directions handle velocity.

**4. Performance & Security**
*   **I/O and Object Creation:** As mentioned, moving the font creation out of the loop is critical for maintaining a stable frame rate.

**Suggested Improvements Summary:**
*   Replace the `STATE` dictionary with a class.
*   Move `pygame.font.SysFont` initialization outside the loop.
*   Simplify `math.sqrt` to `abs()`.
*   Replace magic numbers with descriptive constants.
*   Rename functions to be semantically meaningful.