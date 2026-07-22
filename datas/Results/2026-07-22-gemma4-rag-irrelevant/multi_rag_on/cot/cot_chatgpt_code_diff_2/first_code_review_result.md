### Code Review

**Naming Conventions**
*   **`do_everything()`**: Vague and non-descriptive. This function handles event processing, state updates, and timing; it should be renamed to something like `update_game_state()`.
*   **`draw_stuff()`**: Vague. Rename to `render_frame()` or `draw_game()`.
*   **`STATE`**: While descriptive of its purpose, using a global dictionary for state management is generally discouraged in favor of a class or a structured state object.

**Software Engineering Standards**
*   **Global State**: The reliance on a global `STATE` dictionary makes the code harder to test and maintain. Consider encapsulating the game state in a class.
*   **Modularity**: The `do_everything` function violates the Single Responsibility Principle by mixing input handling, time calculation, and visual state updates.

**Logic & Correctness**
*   **`move_player` complexity**: The use of `int(math.sqrt(STATE["velocity"] ** 2))` and `STATE["velocity"] or 1` is unnecessarily complex and obscures the intent. Use simple addition/subtraction.
*   **`do_everything` call site**: The function is called inside the event loop. This means the game state (score and color) updates multiple times per frame if multiple events occur, or not at all if no events occur. Timing and state updates should happen once per frame outside the event loop.

**Performance & Security**
*   **Font Initialization**: `pygame.font.SysFont(None, 24)` is called every single frame inside `draw_stuff()`. This is a significant performance bottleneck; initialize the font once outside the main loop.

**Readability & Consistency**
*   **Magic Numbers**: Numbers like `57` (clock tick), `10`, and `15` (circle radius) should be defined as named constants at the top of the file.