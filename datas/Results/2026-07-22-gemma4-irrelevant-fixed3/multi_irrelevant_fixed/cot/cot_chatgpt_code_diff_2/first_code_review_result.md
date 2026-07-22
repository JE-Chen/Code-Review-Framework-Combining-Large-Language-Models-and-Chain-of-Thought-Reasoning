### Code Review

**Naming Conventions**
*   **`do_everything()`**: This function name is too vague. It handles input, timing, and state updates. Suggest renaming to `update_game_state()`.
*   **`draw_stuff()`**: This name is non-descriptive. Suggest renaming to `render_frame()`.

**Software Engineering Standards**
*   **Global State**: The use of a global `STATE` dictionary makes the code harder to test and maintain. Consider encapsulating game state into a class.
*   **Modularity**: `do_everything()` mixes input handling with game logic and timing. These should be separated into distinct functions.

**Logic & Correctness**
*   **`move_player()` complexity**: The use of `int(math.sqrt(STATE["velocity"] ** 2))` and `STATE["velocity"] or 1` is unnecessarily complex and inconsistent. Use `STATE["velocity"]` directly for all directions to ensure predictable movement.
*   **`do_everything()` call frequency**: This function is called inside the event loop. This means game logic (like score increments and color shifts) only triggers when an event occurs, rather than every frame. It should be moved to the main loop.

**Performance & Security**
*   **Font Initialization**: `pygame.font.SysFont(None, 24)` is called every frame inside `draw_stuff()`. This is a significant performance bottleneck. Initialize the font once outside the main loop.

**Readability & Consistency**
*   **Magic Numbers**: Values like `57` (clock tick) and `10` (circle radius) should be defined as named constants at the top of the file.