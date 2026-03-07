### Code Smell Type: Global Variables
**Problem Location:**  
All global variables defined at module level (e.g., `screen`, `playerX`, `playerY`, `vx`, `vy`, `enemyList`, `scoreValue`, `runningGame`, `WIDTH`, `HEIGHT`, `PLAYER_SIZE`, `ENEMY_SIZE`, `SPEED`).

**Detailed Explanation:**  
Global state creates tight coupling, makes code harder to test, and increases the risk of unintended side effects. For example:
- `enemyList` is mutated by `initGame` and `checkCollision` without clear ownership.
- `playerX`/`playerY` are modified by `movePlayer` and boundary checks, but their state is scattered across functions.
- Global `runningGame` requires manual synchronization in `mainLoop`.
This violates encapsulation principles and impedes scalability (e.g., adding multiplayer would require massive rework).

**Improvement Suggestions:**  
Encapsulate game state in a class:
```python
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.player = Player(200, 200)
        self.enemies = [Enemy() for _ in range(7)]
        self.score = 0
        self.running = True

class Player:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.vx, self.vy = 0, 0

class Enemy:
    def __init__(self):
        self.x = random.randint(0, WIDTH - ENEMY_SIZE)
        self.y = random.randint(0, HEIGHT - ENEMY_SIZE)
```
Refactor all logic to operate on `Game` instance instead of globals.

**Priority Level:** High

---

### Code Smell Type: Violation of Single Responsibility Principle (SRP)
**Problem Location:**  
`movePlayer` (handles input, movement, and boundary checks) and `checkCollision` (checks collision and updates score/enemy positions).

**Detailed Explanation:**  
- `movePlayer` has 3 distinct responsibilities: 
  1. Input handling (`keys` checks)
  2. Position calculation (`playerX += vx`)
  3. Boundary enforcement (clamping logic).
- `checkCollision` mixes collision detection with game state mutation (incrementing `scoreValue` and resetting enemies).
This makes functions harder to test, modify, or reuse. For example, changing boundary logic requires modifying `movePlayer` instead of a dedicated utility.

**Improvement Suggestions:**  
Split responsibilities:
```python
def handle_input(keys, player):
    player.vx = -SPEED if keys[pygame.K_LEFT] else (SPEED if keys[pygame.K_RIGHT] else 0)
    player.vy = -SPEED if keys[pygame.K_UP] else (SPEED if keys[pygame.K_DOWN] else 0)

def update_player(player, width, height, size):
    player.x += player.vx
    player.y += player.vy
    player.x = max(0, min(player.x, width - size))
    player.y = max(0, min(player.y, height - size))

def detect_collisions(player, enemies):
    return [enemy for enemy in enemies 
            if (player.x < enemy.x + ENEMY_SIZE and 
                player.x + PLAYER_SIZE > enemy.x and
                player.y < enemy.y + ENEMY_SIZE and
                player.y + PLAYER_SIZE > enemy.y)]
```
Then in `mainLoop`:
```python
colliding_enemies = detect_collisions(player, enemies)
for enemy in colliding_enemies:
    score += 1
    enemy.reset()
```

**Priority Level:** High

---

### Code Smell Type: Poor Naming Conventions
**Problem Location:**  
Variables `vx`, `vy`, `e`, `scoreValue`, `runningGame`.

**Detailed Explanation:**  
- `vx`/`vy`: Abbreviated and unclear without context (better as `player_velocity_x`).
- `e`: Overused single-letter variable in enemy loop (should be `enemy`).
- `scoreValue`: Redundant (use `score`).
- `runningGame`: Ambiguous (should be `is_running` or `game_active`).
Poor names increase cognitive load and reduce readability. For example, `e[0]` and `e[1]` in `checkCollision` require mental mapping to coordinates.

**Improvement Suggestions:**  
Rename for clarity:
```python
# Replace:
#   vx, vy -> player_velocity_x, player_velocity_y
#   e -> enemy
#   scoreValue -> score
#   runningGame -> game_active
```
Prefer descriptive names like `enemy_position` over `e`.

**Priority Level:** Medium

---

### Code Smell Type: Lack of Documentation
**Problem Location:**  
All functions (`initGame`, `movePlayer`, `drawEverything`, etc.) lack docstrings.

**Detailed Explanation:**  
Missing documentation forces readers to reverse-engineer logic. For example:
- What does `movePlayer` expect for `keys`?
- How does `checkCollision` handle multiple collisions?
- What units are used for `WIDTH`/`HEIGHT`?
This hinders onboarding and maintenance, especially for new contributors.

**Improvement Suggestions:**  
Add concise docstrings:
```python
def movePlayer(keys: dict) -> None:
    """Updates player velocity based on pressed keys and enforces boundaries."""
    ...
```
Include parameter/return types and key behavior notes.

**Priority Level:** Medium

---

### Code Smell Type: Inconsistent Constants Usage
**Problem Location:**  
`WIDTH`/`HEIGHT` used in `initGame` but `PLAYER_SIZE` and `ENEMY_SIZE` not consistently applied for enemy boundaries.

**Detailed Explanation:**  
- Enemies are initialized with `WIDTH-ENEMY_SIZE` (correct), but the collision logic uses `ENEMY_SIZE` directly.
- Player boundaries use `WIDTH-PLAYER_SIZE` (correct), but the constant `PLAYER_SIZE` is not used for the player's drawing rectangle (redundant `30`).
This inconsistency risks bugs if constants change. For example, if `PLAYER_SIZE` is updated, the boundary condition might break.

**Improvement Suggestions:**  
Use constants consistently:
```python
# In drawEverything:
pygame.draw.rect(screen, (0, 255, 0), (playerX, playerY, PLAYER_SIZE, PLAYER_SIZE))
# Replace hardcoded 30 with PLAYER_SIZE
```
Ensure all size-related calculations use named constants.

**Priority Level:** Low

---

### Code Smell Type: Missing Unit Tests
**Problem Location:**  
No test cases or test framework (e.g., pytest) present.

**Detailed Explanation:**  
Critical game logic (player movement, collision) lacks automated verification. For example:
- No test for boundary enforcement at edges.
- No test for collision scoring.
- No test for enemy reset after collision.
This increases regression risk and reduces confidence in changes.

**Improvement Suggestions:**  
Add minimal unit tests:
```python
def test_player_boundary():
    player = Player(0, 0)
    player.vx = -5
    player.x = -10
    update_player(player, WIDTH, HEIGHT, PLAYER_SIZE)
    assert player.x == 0
```
Focus on boundary cases and core logic.

**Priority Level:** Medium