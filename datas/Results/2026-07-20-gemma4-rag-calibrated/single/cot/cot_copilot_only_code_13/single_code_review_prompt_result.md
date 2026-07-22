Overall, the code is a functional prototype, but it is written as a procedural script rather than a structured application. The primary issue is the heavy reliance on global state, which makes the code difficult to test, scale, or debug.

### 1. Linter & Style Messages (PEP 8)
*   **Naming Conventions:** Python uses `snake_case` for variables and functions.
    *   *Issue:* `playerX`, `enemyList`, `scoreValue`, `runningGame`, `initGame` use `camelCase`.
    *   *Fix:* Rename to `player_x`, `enemy_list`, `score_value`, etc.
*   **Whitespace:** There are several instances of multiple statements on one line.
    *   *Issue:* `if playerX < 0: playerX = 0`
    *   *Fix:* Move the action to a new indented line for readability.
*   **Constant Placement:** Constants are defined in the middle of the file.
    *   *Fix:* Move `WIDTH`, `HEIGHT`, etc., to the top of the file.

### 2. Code Smells
*   **Global State Abuse:** The use of the `global` keyword in almost every function is a major red flag.
    *   *Why it matters:* Global variables create hidden dependencies. If the game grows, tracking which function modified a variable becomes a nightmare.
    *   *Fix:* Encapsulate the game state into a `Game` class or pass objects as arguments to functions.
*   **Magic Numbers/Tuples:** The `enemyList` stores enemies as simple lists `[x, y]`.
    *   *Why it matters:* `e[0]` and `e[1]` are not descriptive. It is unclear that `0` is X and `1` is Y without reading the initialization logic.
    *   *Fix:* Use `pygame.Rect` objects for enemies and the player. This provides built-in collision methods (e.g., `rect.colliderect()`).
*   **Inefficient Resource Loading:** `pygame.font.SysFont(None, 36)` is called inside `drawEverything()`.
    *   *Why it matters:* This creates a new font object 30 times per second, which is a significant performance hit and memory leak risk.
    *   *Fix:* Initialize the font once in `initGame()` and store it in a variable.

### 3. Best Practices
*   **Collision Logic:** The manual AABB (Axis-Aligned Bounding Box) calculation in `checkCollision` is redundant.
    *   *Improvement:* Use `pygame.Rect`. It simplifies the logic from 4 lines of comparisons to one: `if player_rect.colliderect(enemy_rect):`.
*   **Input Handling:** The movement logic is tied directly to the frame rate.
    *   *Improvement:* While `clock.tick(30)` helps, consider using a Delta Time ($\Delta t$) approach for movement to ensure consistent speed across different hardware.
*   **Modularization:** The game logic (collision/movement) is mixed with the rendering logic.
    *   *Improvement:* Separate the "Update" phase from the "Draw" phase.

---

### Suggested Refactoring (Conceptual)

Instead of global variables, structure the code like this:

```python
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.player = pygame.Rect(200, 200, PLAYER_SIZE, PLAYER_SIZE)
        self.enemies = [pygame.Rect(random.randint(0, WIDTH-ENEMY_SIZE), 
                                    random.randint(0, HEIGHT-ENEMY_SIZE), 
                                    ENEMY_SIZE, ENEMY_SIZE) for _ in range(7)]
        self.score = 0
        self.font = pygame.font.SysFont(None, 36)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        # Update self.player.x and self.player.y based on keys...

    def update(self):
        for enemy in self.enemies:
            if self.player.colliderect(enemy):
                self.score += 1
                enemy.x = random.randint(0, WIDTH-ENEMY_SIZE)
                enemy.y = random.randint(0, HEIGHT-ENEMY_SIZE)

    def draw(self):
        self.screen.fill((0, 0, 0))
        pygame.draw.rect(self.screen, (0, 255, 0), self.player)
        for enemy in self.enemies:
            pygame.draw.rect(self.screen, (255, 0, 0), enemy)
        # Render score using self.font...
        pygame.display.flip()
```

### Summary of Strengths
*   **Correct Game Loop:** The basic structure (Event $\rightarrow$ Update $\rightarrow$ Draw $\rightarrow$ Tick) is correctly implemented.
*   **Boundary Checking:** The code correctly prevents the player from leaving the screen.
*   **Clean Entry Point:** The use of `if __name__ == "__main__":` is a professional practice.