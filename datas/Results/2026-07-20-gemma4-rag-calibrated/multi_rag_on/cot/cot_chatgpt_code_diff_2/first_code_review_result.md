### Code Review

**1. Readability & Naming**
*   **Vague Naming:** `do_everything()` and `draw_stuff()` are non-descriptive. Rename them to reflect their actual purpose (e.g., `update_game_state()` and `render_frame()`).
*   **Magic Numbers:** The code contains several hard-coded values (e.g., `clock.tick(57)`, `delta * 10 % 7`, `10 + STATE["score"] % 15`). These should be defined as named constants at the top of the file.

**2. Software Engineering Standards**
*   **Shared Mutable State:** The use of a global `STATE` dictionary introduces hidden coupling and makes the code difficult to test or extend. Encapsulate the game state into a class or pass it explicitly to functions.
*   **Modularity:** The main game loop is written at the top level of the script. Wrap the execution logic in a `main()` function to prevent global scope pollution.

**3. Logic & Correctness**
*   **Redundant Logic:** In `move_player`, `int(math.sqrt(STATE["velocity"] ** 2))` is a computationally expensive way to write `abs(STATE["velocity"])`.
*   **Unstable Logic:** `STATE["player"][1] += STATE["velocity"] or 1` creates inconsistent behavior; if velocity is 0, the player moves by 1, but in other directions, they stay still.

**4. Performance & Security**
*   **Resource Management:** `pygame.font.SysFont(None, 24)` is called every single frame inside `draw_stuff()`. This is a significant performance bottleneck. Initialize the font once outside the loop.

**5. Summary of Suggestions**
*   Replace the global `STATE` dictionary with a class.
*   Move font initialization out of the render loop.
*   Simplify the mathematical expressions in `move_player`.
*   Replace magic numbers with descriptive constants.