### Diff #1

#### Summary
This PR introduces a new Python script named `game.py`, which appears to be a simple game using the Pygame library. The script initializes a window, handles player movement based on keyboard inputs, updates a score, and renders the player's position and score on the screen.

#### Linting Issues
- **E302**: Expected 2 blank lines, found 1.
  - **File:** `game.py`
  - **Line:** 19
  - **Correction:** Add a blank line after importing modules.
  
- **W503**: Line break occurred before a binary operator.
  - **File:** `game.py`
  - **Lines:** 40, 53, 63, 70
  - **Correction:** Remove the line breaks before the operators.

#### Code Smells
- **Long Functions:** The function `do_everything` contains multiple responsibilities including updating velocity, score, and color. It should be refactored into smaller, more focused functions.
  - **Issue:** Multiple responsibilities within `do_everything`.
  - **Recommendation:** Break down `do_everything` into separate functions like `update_velocity`, `update_score`, and `update_color`.

- **Poor Naming:** The variable names like `STATE` could be more descriptive to improve understanding.
  - **Issue:** Generic variable name `STATE`.
  - **Recommendation:** Rename to something like `game_state` or `app_state`.