### Diff #1

#### Summary
This PR introduces a new Python script named `game.py`, which appears to be a basic implementation of a simple game using the Pygame library. The game involves moving a green rectangle (player) around the screen, avoiding red rectangles (enemies), and scoring points when enemies are hit.

#### Linting Issues
- **Unused variable 'scoreValue'**: Line 26
  - The variable `scoreValue` is defined but never used.
  - **Correction**: Remove the unused variable or use it within the game logic.
  
- **Global variables**: Multiple global variables are declared at the top of the file.
  - While not necessarily an error, excessive use of global variables can lead to harder-to-maintain code.
  - **Correction**: Consider encapsulating state within classes or passing parameters where needed.

#### Code Smells
- **Long function 'mainLoop'**: Lines 34-60
  - This function handles all game logic, including initialization, event handling, movement, collision detection, and drawing.
  - **Problematic**: It violates the Single Responsibility Principle, making the code hard to read and test.
  - **Recommendation**: Break down `mainLoop` into smaller functions, each responsible for a single aspect of the game loop (e.g., handling events, updating game state, rendering).

- **Hardcoded values**: Many constants like `WIDTH`, `HEIGHT`, `PLAYER_SIZE`, etc., are hardcoded throughout the code.
  - **Problematic**: Makes the code less flexible and harder to change.
  - **Recommendation**: Define these constants in a configuration dictionary or module and import them where needed.

- **No comments or docstrings**: There are no comments explaining the purpose of functions or any other significant parts of the code.
  - **Problematic**: Reduces code readability and maintainability.
  - **Recommendation**: Add clear comments and docstrings to explain complex logic or non-obvious decisions.