### Diff #1

---

### **Summary**
- **Purpose**: Implements a basic Pygame-based game where the player moves a green square to avoid red enemies. Upon collision, the enemy respawns, and the score increments.
- **Scope**: Entirely contained in `game.py`, covering initialization, player movement, collision detection, rendering, and the main game loop.
- **Plain-language explanation**: A simple game where you control a green square with arrow keys. Red squares appear randomly on screen; touching one increases your score and makes the red square reappear elsewhere.

---

### **Linting Issues**
- **Line length violations** (all in `checkCollision`):
  - Condition spans 4 lines but exceeds 79 characters on the first line (e.g., `playerX < e[0] + ENEMY_SIZE and ...`).  
  *Suggestion*: Break condition into shorter, more readable lines without sacrificing clarity.
- **Inconsistent indentation** (in `checkCollision`):
  - Second line of condition indented by 4 spaces, but subsequent lines align with the *first* condition (not the opening parenthesis).  
  *Suggestion*: Align all condition lines with the opening parenthesis for consistency.

---

### **Code Smells**
- **Heavy global variable usage** (e.g., `playerX`, `enemyList`, `scoreValue`):
  - *Why problematic*: Creates hidden dependencies, complicates testing, and risks accidental state corruption. Functions like `movePlayer` and `checkCollision` rely on global state instead of explicit inputs/outputs.
  - *Recommendation*: Encapsulate state in a `Game` class. Example: Replace `playerX` with `self.player_x` and pass state via method parameters.
  
- **Magic numbers** (e.g., `WIDTH = 640`, `HEIGHT = 480`):
  - *Why problematic*: Hardcoded values lack context. Changing screen dimensions requires manual updates across multiple lines.
  - *Recommendation*: Define constants clearly (already done for `WIDTH`/`HEIGHT`), but add comments explaining *why* these values were chosen (e.g., `WIDTH = 640  # Standard 4:3 resolution`).

- **Inefficient collision logic** (`checkCollision`):
  - *Why problematic*: Recalculates collision for every enemy *every frame*, even when enemies aren’t moving. This is unnecessary for static enemies.
  - *Recommendation*: Optimize by skipping collision checks if enemies haven’t moved (e.g., track last update time). For simplicity, consider using Pygame’s `Rect` for collision (reduces manual math).

- **Poor error handling**:
  - *Why problematic*: No validation for `enemyList` (e.g., empty list) or input handling (e.g., `pygame.key.get_pressed()` might return unexpected keys).
  - *Recommendation*: Add guard clauses (e.g., `if not enemyList: continue`) and validate user input. Use `pygame.event` for keyboard events instead of `keys` for better control.