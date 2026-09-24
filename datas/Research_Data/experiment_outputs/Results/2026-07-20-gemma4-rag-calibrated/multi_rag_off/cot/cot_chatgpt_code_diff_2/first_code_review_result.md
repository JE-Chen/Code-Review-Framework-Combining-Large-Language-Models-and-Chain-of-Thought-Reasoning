### Code Review

**Naming Conventions**
*   `do_everything()`: The function name is too vague. It handles input, timing, and state updates; it should be renamed to something like `update_game_state()`.
*   `draw_stuff()`: Vague naming. Suggest `render_frame()` or `draw_game()`.

**Software Engineering Standards**
*   **Global State**: The use of a global `STATE` dictionary makes the code harder to test and maintain. Consider encapsulating game state into a class.
*   **Modularity**: `do_everything()` violates the Single Responsibility Principle by mixing event handling, delta-time calculation, and visual updates.

**Logic & Correctness**
*   **Redundant Math**: In `move_player`, `int(math.sqrt(STATE["velocity"] ** 2))` is a computationally expensive way to write `abs(STATE["velocity"])`.
*   **Inconsistent Movement**: `STATE["player"][1] += STATE["velocity"] or 1` introduces a magic number (`1`) that triggers only when velocity is 0, creating inconsistent movement behavior compared to other directions.
*   **Resource Management**: `pygame.font.SysFont(None, 24)` is called every frame inside `draw_stuff()`. This is a significant performance bottleneck; the font should be initialized once outside the main loop.

**Performance & Security**
*   **Frame Rate**: `clock.tick(57)` is an unusual value. Unless specifically required for a mechanic, standard values like 60 are preferred for consistency.