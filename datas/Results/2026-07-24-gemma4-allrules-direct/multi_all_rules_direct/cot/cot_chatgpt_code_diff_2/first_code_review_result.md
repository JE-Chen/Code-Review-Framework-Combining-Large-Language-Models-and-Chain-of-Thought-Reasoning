### Code Review

**Naming Conventions**
*   **`do_everything()`**: This name is too vague and does not describe the function's purpose. It should be renamed to reflect that it handles state updates and event processing (e.g., `update_game_state`).
*   **`draw_stuff()`**: Similarly, this is non-descriptive. A name like `render_frame` or `draw_game` is preferred.

**Software Engineering Standards**
*   **Shared Mutable State**: The use of a global `STATE` dictionary introduces hidden coupling and makes the code harder to test and maintain. Consider encapsulating the game state in a class or passing it explicitly to functions.
*   **Single Responsibility Principle**: `do_everything()` violates this by handling input events, calculating delta time, updating the score, and mutating colors all in one place. These should be split into focused functions.

**Logic & Correctness**
*   **Redundant Logic**: In `move_player`, `int(math.sqrt(STATE["velocity"] ** 2))` is a computationally expensive way to write `abs(STATE["velocity"])`.
*   **Implicit Truthiness**: The expression `STATE["velocity"] or 1` in `move_player` relies on implicit truthiness. Use an explicit comparison (e.g., `if STATE["velocity"] == 0:`) to improve clarity.

**Performance & Security**
*   **Resource Management**: `pygame.font.SysFont(None, 24)` is called every single frame inside `draw_stuff()`. This is a significant performance bottleneck; the font should be initialized once outside the main loop.

**Readability & Consistency**
*   **Magic Numbers**: Numbers like `57` (clock tick), `10`, `15`, and `7` are used without explanation. These should be defined as named constants at the top of the file.