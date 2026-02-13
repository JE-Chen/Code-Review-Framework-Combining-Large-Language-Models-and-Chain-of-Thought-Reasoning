### Code Smell Type: Global Variables
**Problem Location**:  
Top-level variables (`screen`, `playerX`, `playerY`, `vx`, `vy`, `enemyList`, `scoreValue`, `runningGame`) and `global` declarations in `movePlayer`, `checkCollision`, and other functions.

**Detailed Explanation**:  
Global state creates hidden dependencies, complicates testing, and increases coupling. Changes to one global variable (e.g., `enemyList`) can unexpectedly affect unrelated functions. For example, `checkCollision` modifies `enemyList` directly while iterating, risking subtle bugs if the list structure changes. This violates encapsulation and makes the codebase fragile for future modifications.

**Improvement Suggestions**:  
Encapsulate game state in a `Game` class. Replace global variables with instance attributes. Example:
```python
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.player = Player(100, 100)
        self.enemies = [Enemy() for _ in range(NUMBER_OF_ENEMIES)]
        self.score = 0
        self.running = True

    def move_player(self, keys):
        # Update player position using self.player
```

**Priority Level**: High  
*(Critical for maintainability and testability; blocks future refactoring)*

---

### Code Smell Type: Magic Number
**Problem Location**:  
`for i in range(9):` in `initGame()`.

**Detailed Explanation**:  
The number `9` lacks context. If the enemy count needs to change (e.g., for balancing), developers must search the codebase for all occurrences. This violates the "Don’t Repeat Yourself" principle and increases bug risk (e.g., forgetting to update the number elsewhere).

**Improvement Suggestions**:  
Define a constant at the module level:
```python
NUMBER_OF_ENEMIES = 9
# Then use: for _ in range(NUMBER_OF_ENEMIES):
```

**Priority Level**: Low  
*(Minor issue in a small game, but improves clarity)*

---

### Code Smell Type: Unmaintainable Enemy Representation
**Problem Location**:  
Enemy data stored as `[x, y]` lists in `enemyList`.

**Detailed Explanation**:  
Using raw lists for enemy data reduces readability and safety. The collision logic relies on index-based access (`e[0]`, `e[1]`), which is error-prone. If the enemy structure changes (e.g., adding a health field), all related code must be updated manually. This violates the "self-documenting code" principle.

**Improvement Suggestions**:  
Use a dedicated `Enemy` class or `namedtuple`:
```python
from collections import namedtuple
Enemy = namedtuple("Enemy", ["x", "y"])

# Or a class:
class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
```
Then update collision logic to use `e.x` and `e.y`.

**Priority Level**: Medium  
*(Blocks scalability and increases bug risk as features grow)*

---

### Code Smell Type: Missing Documentation
**Problem Location**:  
No docstrings or comments for functions (`initGame`, `movePlayer`, etc.) or key variables.

**Detailed Explanation**:  
The code lacks explanations for *why* logic exists. For example, `checkCollision`’s AABB condition is standard but unexplained. New developers must reverse-engineer intent, slowing onboarding. This also impedes test coverage (tests require understanding the behavior).

**Improvement Suggestions**:  
Add docstrings explaining purpose, parameters, and behavior:
```python
def check_collision(self) -> None:
    """Check if player collides with any enemy. On hit, reset enemy position and increment score."""
    for enemy in self.enemies:
        if self.player.collides_with(enemy):
            self.score += 1
            enemy.reset()
```

**Priority Level**: Medium  
*(Critical for long-term maintainability but not an immediate bug)*

---

### Code Smell Type: Inconsistent Naming
**Problem Location**:  
Variables like `vx`/`vy` (velocity) and `e` (enemy) use non-descriptive names.

**Detailed Explanation**:  
`vx`/`vy` imply "velocity" but lack context (e.g., `player_velocity_x`). The shorthand `e` for enemy is acceptable in tight loops but inconsistent with the rest of the code. Naming should clarify intent to reduce cognitive load.

**Improvement Suggestions**:  
Use explicit names:
```python
# Instead of:
#   vx = -SPEED
# Use:
self.player_velocity_x = -SPEED
```
For loops, prefer `enemy` over `e`:
```python
for enemy in self.enemies:
    # ...
```

**Priority Level**: Low  
*(Minor readability issue; low impact on correctness)*

---

### Summary of Fixes Priority
| Code Smell                | Priority |
|---------------------------|----------|
| Global Variables          | High     |
| Unmaintainable Enemy Data | Medium   |
| Missing Documentation     | Medium   |
| Magic Number              | Low      |
| Inconsistent Naming       | Low      |