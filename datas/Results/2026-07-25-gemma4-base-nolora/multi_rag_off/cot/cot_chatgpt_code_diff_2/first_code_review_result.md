### Code Review

**Naming Conventions**
*   **`do_everything()`**: The function name is too vague. It handles input, timing, score updates, and color shifts. Suggest splitting into `handle_input()` and `update_game_state()`.
*   **`draw_stuff()`**: Too generic. Suggest `render()` or `draw_game()`.
*   **`STATE`**: While descriptive of its purpose, using a global dictionary for state management makes the code harder to test and maintain. Consider a `GameState` class.

**Software Engineering Standards**
*   **Global State**: The reliance on a global `STATE` dictionary creates tight coupling. Pass state as arguments to functions to improve modularity.
*   **Resource Management**: `pygame.font.SysFont` is called every frame inside `draw_stuff()`. This is a significant performance bottleneck; initialize the font once outside the main loop.

**Logic & Correctness**
*   **Over-complicated Math**: In `move_player`, `int(math.sqrt(STATE["velocity"] ** 2))` is functionally equivalent to `abs(STATE["velocity"])`. This adds unnecessary overhead and reduces readability.
*   **Inconsistent Movement**: `STATE["player"][1] += STATE["velocity"] or 1` contains a fallback to `1` if velocity is `0`. This creates inconsistent behavior compared to the X-axis movement.
*   **Score Logic**: `STATE["score"] += int(delta * 10) % 7` results in very erratic score increments based on frame timing.

**Readability & Consistency**
*   **Magic Numbers**: Numbers like `57` (clock tick), `10`, `15`, and `7` are used without explanation. Define these as constants (e.g., `FPS = 60`).
*   **Formatting**: The code is generally well-indented, but the logic within `do_everything` mixes event handling with frame-based updates, which is confusing.

**Performance & Security**
*   **Font Rendering**: As mentioned, moving `pygame.font.SysFont` out of the loop is critical to prevent memory churn and frame drops.