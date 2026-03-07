### 1. **Global Variables Used**
- **Issue**: Using global variables reduces modularity and testability.
- **Explanation**: Functions like `initGame` and `mainLoop` rely on global state (`playerX`, `enemyList`, etc.) instead of accepting them as parameters.
- **Why It Happens**: The code assumes shared mutable state across functions, which leads to tight coupling.
- **Impact**: Makes unit testing hard and increases risk of side effects.
- **Fix Example**:
  ```python
  # Before
  def movePlayer():
      global playerX, playerY
      playerX += vx

  # After
  def movePlayer(player_x, player_y, velocity_x, velocity_y):
      return player_x + velocity_x, player_y + velocity_y
  ```

---

### 2. **Magic Numbers in Screen Dimensions**
- **Issue**: Hardcoded numbers like `WIDTH=640` and `HEIGHT=480`.
- **Explanation**: These values are scattered without explanation or reuse.
- **Why It Happens**: Quick prototyping or lack of abstraction.
- **Impact**: Difficult to change layout or scale later.
- **Fix Example**:
  ```python
  # Before
  screen = pygame.display.set_mode((640, 480))

  # After
  SCREEN_WIDTH = 640
  SCREEN_HEIGHT = 480
  screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
  ```

---

### 3. **Inconsistent Naming Style**
- **Issue**: Mix of snake_case and camelCase variable names.
- **Explanation**: `playerX` vs `enemyList` makes code less predictable.
- **Why It Happens**: Lack of enforced style guide.
- **Impact**: Reduces readability for new developers.
- **Fix Example**:
  ```python
  # Before
  playerX = 100
  enemyList = []

  # After
  player_x = 100
  enemy_list = []
  ```

---

### 4. **Tight Coupling Between Game Logic and Drawing**
- **Issue**: Drawing functions directly access global state.
- **Explanation**: `drawEverything()` uses `screen` and `enemyList` directly.
- **Why It Happens**: No clear separation between rendering and logic.
- **Impact**: Harder to swap rendering engines or mock during tests.
- **Fix Example**:
  ```python
  # Before
  def drawEverything():
      screen.fill((0, 0, 0))

  # After
  class Renderer:
      def __init__(self, surface):
          self.surface = surface

      def render(self, game_state):
          self.surface.fill((0, 0, 0))
  ```

---

### 5. **Imperative Programming Style**
- **Issue**: Code uses imperative patterns instead of functional or object-oriented approaches.
- **Explanation**: Direct mutation of game state instead of returning updated values.
- **Why It Happens**: Legacy or procedural thinking.
- **Impact**: Less flexible and harder to compose.
- **Fix Example**:
  ```python
  # Before
  player_x += speed

  # After
  def update_position(current_pos, delta):
      return current_pos + delta
  ```

---

### 6. **Hardcoded Color & Position Values**
- **Issue**: Colors and screen positions are hardcoded.
- **Explanation**: Makes UI tweaks or responsive layouts difficult.
- **Why It Happens**: Rapid development without abstraction.
- **Impact**: Reduces flexibility and increases maintenance cost.
- **Fix Example**:
  ```python
  # Before
  text_color = (255, 255, 255)
  score_pos = (10, 10)

  # After
  TEXT_COLOR = (255, 255, 255)
  SCORE_POSITION = (10, 10)
  ```

---

### 7. **Missing Documentation**
- **Issue**: Functions lack docstrings or inline comments.
- **Explanation**: Future developers cannot easily understand purpose or usage.
- **Why It Happens**: Assumption that code speaks for itself.
- **Impact**: Slows down onboarding and refactoring.
- **Fix Example**:
  ```python
  def move_player(x, y, dx, dy):
      """Moves player by given deltas."""
      return x + dx, y + dy
  ```

---

### 8. **Long Functions Violating Single Responsibility Principle**
- **Issue**: `movePlayer()` and `checkCollision()` handle too many tasks.
- **Explanation**: They mix logic, movement, and collision detection.
- **Why It Happens**: Lack of decomposition.
- **Impact**: Hard to test and modify.
- **Fix Example**:
  ```python
  # Before
  def move_player():
      ... # Movement + Collision Check

  # After
  def apply_movement(x, y, dx, dy):
      return x + dx, y + dy

  def check_collision(x, y, enemies):
      ...
  ```

---

### 9. **Redundant Boundary Checks**
- **Issue**: Repeated checks for screen boundaries.
- **Explanation**: Logic duplicated across multiple places.
- **Why It Happens**: Lack of reusable utilities.
- **Impact**: Increases chances of bugs when updating one side.
- **Fix Example**:
  ```python
  def clamp(value, min_val, max_val):
      return max(min_val, min(value, max_val))

  player_x = clamp(player_x, 0, SCREEN_WIDTH)
  ```

---

### 10. **Unused Import**
- **Issue**: `import sys` is not used anywhere.
- **Explanation**: Clutters code and indicates incomplete cleanup.
- **Why It Happens**: Copy-paste or oversight.
- **Impact**: Minor but reduces cleanliness.
- **Fix Example**:
  ```python
  # Remove unused import
  # import sys
  ```

---

### ✅ Best Practices Recap

| Area | Suggestion |
|------|------------|
| **State Management** | Encapsulate game logic in a class with controlled access. |
| **Constants** | Replace magic numbers with named constants. |
| **Naming** | Stick to snake_case for consistency. |
| **Separation of Concerns** | Split input handling, game logic, and rendering. |
| **Code Style** | Prefer declarative or functional patterns over imperative loops. |
| **Testing** | Pass dependencies explicitly to isolate behavior. |

By addressing these points, your codebase becomes more modular, readable, and maintainable.