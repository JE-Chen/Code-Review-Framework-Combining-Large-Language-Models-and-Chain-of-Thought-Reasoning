### Diff #1

---

#### **Summary**  
This diff implements a simple Pygame-based game with player movement, enemy generation, collision detection, and score tracking. The changes affect the core game logic: initialization (`initGame`), player input handling (`movePlayer`), rendering (`drawEverything`), collision checks (`checkCollision`), and the main game loop (`mainLoop`). The game features a green player square moving with arrow keys, red enemy squares that respawn on collision, and a score counter. Non-experts would understand it as a basic "collect the enemies" game where the player avoids obstacles while earning points.

---

#### **Linting Issues**  
- **Unused Variable**: `i` in `initGame`'s loop is unused.  
  *Suggestion*: Replace `for i in range(7):` → `for _ in range(7):` (avoids confusion about loop variable).  
- **Magic Numbers**: Hard-coded values like `0`, `30`, `25`, and `5` appear in conditions (e.g., `playerX < e[0] + ENEMY_SIZE`).  
  *Suggestion*: Use named constants (e.g., `ENEMY_SIZE`) consistently. *Note: `ENEMY_SIZE` is defined, but the condition uses it correctly—this is a minor issue.*  
- **Inconsistent Spacing**: Line `if playerX < 0: playerX = 0` lacks spaces around operators.  
  *Suggestion*: Format as `if playerX < 0: playerX = 0` → `if playerX < 0: playerX = 0` (standard style).  

---

#### **Code Smells**  
- **Overuse of Global Variables**:  
  *Problem*: Critical state (`playerX`, `enemyList`, `scoreValue`, etc.) is stored globally. This couples functions tightly and complicates testing/refactoring.  
  *Improvement*: Encapsulate state in a `Game` class (e.g., `self.player_x`, `self.enemies`).  

- **Primitive Obsession**:  
  *Problem*: Enemies are stored as raw lists (`[x, y]`), making collision logic error-prone.  
  *Improvement*: Replace with a simple `Enemy` class (e.g., `enemy = Enemy(x, y)`) or use `namedtuple`.  

- **Long Function**: `checkCollision` handles both collision detection *and* enemy respawn logic.  
  *Problem*: Violates single responsibility principle; harder to debug or extend.  
  *Improvement*: Split into `check_collision()` and `respawn_enemy(enemy)`.  

- **Hardcoded Game Dimensions**:  
  *Problem*: `WIDTH=640`, `HEIGHT=480` are defined but not used in all contexts (e.g., `WIDTH-ENEMY_SIZE` in `initGame`).  
  *Improvement*: Use `WIDTH`/`HEIGHT` consistently for all boundaries.  

- **Tight Coupling**: `movePlayer` directly mutates global `playerX`/`playerY` instead of returning new positions.  
  *Problem*: Breaks separation of concerns; forces global state.  
  *Improvement*: Calculate positions in `movePlayer` and pass to `drawEverything`.