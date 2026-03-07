### Code Quality Review Report

---

#### **1. Global Variables (Rule: `no-global-state`)**
**Issue in Plain English**  
The code relies heavily on global variables (e.g., `playerX`, `enemyList`, `runningGame`), making the program state scattered and hard to manage.  

**Root Cause**  
Game state is defined at the module level instead of being encapsulated within a dedicated object. Functions modify these globals directly, creating hidden dependencies.  

**Impact Assessment**  
- **High severity**: Breaks testability (cannot isolate logic without global setup), increases bug risk (e.g., accidental state corruption), and blocks scalability (e.g., adding multiplayer requires rewriting all state logic).  
- *Example*: `checkCollision` mutates `enemyList` and `scoreValue` without clear ownership, causing fragile cross-function dependencies.  

**Suggested Fix**  
Encapsulate state in a `Game` class:  
```python
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.player = Player(200, 200)
        self.enemies = [Enemy() for _ in range(NUM_ENEMIES)]
        self.score = 0
        self.running = True

# Replace global calls with instance methods:
game = Game()
game.player.move(keys)
game.check_collision()
```

**Best Practice**  
**Encapsulation (SOLID Principle)**: Hide internal state behind class interfaces. Avoid global state to prevent unintended side effects and simplify testing.

---

#### **2. Undescriptive Variable Names (Rule: `bad-variable-names`)**
**Issue in Plain English**  
Short names like `vx` and `vy` lack context, forcing readers to infer meaning from usage.  

**Root Cause**  
Names prioritize brevity over clarity. The code treats `vx`/`vy` as implicit player velocity without explicit naming.  

**Impact Assessment**  
- **Medium severity**: Reduces readability and increases cognitive load. New contributors must reverse-engineer logic (e.g., `vx` could mean *velocity*, *x-position*, or *x-offset*).  
- *Example*: `playerX += vx` is ambiguous without context.  

**Suggested Fix**  
Use explicit names:  
```python
# Before
vx = 5
playerX += vx

# After
player_velocity_x = 5
player_x += player_velocity_x
```

**Best Practice**  
**Naming Conventions**: Names should self-document intent. Prefer `player_velocity_x` over `vx` to eliminate guesswork.

---

#### **3. Magic Number (Rule: `magic-number`)**
**Issue in Plain English**  
The number `7` (enemy count) appears without explanation in `enemyList = [Enemy() for _ in range(7)]`.  

**Root Cause**  
Hardcoded values replace named constants, making code brittle when requirements change.  

**Impact Assessment**  
- **Medium severity**: If enemy count needs adjustment, every occurrence of `7` must be manually updated (risk of missed changes).  
- *Example*: Changing `7` to `5` breaks consistency if other logic assumes `7` enemies.  

**Suggested Fix**  
Define a constant:  
```python
NUM_ENEMIES = 7
enemyList = [Enemy() for _ in range(NUM_ENEMIES)]
```

**Best Practice**  
**Avoid Magic Numbers**: Replace literals with named constants to clarify intent and centralize changes.

---

#### **4. Missing Function Documentation (Rule: `missing-docstrings`)**
**Issue in Plain English**  
Functions like `movePlayer` lack docstrings explaining purpose, parameters, and behavior.  

**Root Cause**  
Documentation is treated as optional rather than a core requirement.  

**Impact Assessment**  
- **Medium severity**: Slows onboarding and increases bug risk (e.g., unclear input format for `keys` dictionary).  
- *Example*: Without docs, a developer might pass `keys` as a list instead of a dict, causing silent failures.  

**Suggested Fix**  
Add concise docstrings:  
```python
def movePlayer(keys: dict) -> None:
    """
    Updates player position based on key presses and enforces screen boundaries.
    
    Args:
        keys: Pygame key dictionary (e.g., pygame.key.get_pressed()).
    """
    # ... implementation ...
```

**Best Practice**  
**Documentation as Code**: Treat docstrings as essential as code. Document *what* the function does, *why*, and *how* to use it.

---

#### **5. Undocumented Data Structure (Rule: `missing-structure-doc`)**
**Issue in Plain English**  
The `enemyList` structure (e.g., `[x, y]` positions) isn’t documented, forcing readers to infer format from code.  

**Root Cause**  
Data contracts are implicit instead of explicit.  

**Impact Assessment**  
- **Low severity**: Causes minor confusion but rarely breaks logic.  
- *Example*: A developer might misread `enemy[0]` as *x-coordinate* instead of *y-coordinate* due to lack of docs.  

**Suggested Fix**  
Document or use structured types:  
```python
# Option 1: Docstring
enemy = {
    "x": 100,  # Enemy X position
    "y": 50,   # Enemy Y position
}

# Option 2: NamedTuple
from collections import namedtuple
Enemy = namedtuple("Enemy", ["x", "y"])
enemy = Enemy(x=100, y=50)
```

**Best Practice**  
**Document Data Contracts**: Explicitly describe data structures to prevent misinterpretation and ensure consistency.

---

### Summary of Critical Improvements
| Issue                  | Priority | Why It Matters                                                                 |
|------------------------|----------|------------------------------------------------------------------------------|
| Global variables       | High     | Breaks testability, scalability, and maintainability.                          |
| Magic numbers/constants| Medium   | Increases risk of inconsistent changes.                                       |
| Poor naming            | Medium   | Slows comprehension and onboarding.                                           |
| Missing documentation  | Medium   | Hinders collaboration and maintenance.                                        |
| Undocumented structures| Low      | Minor readability impact; easy to fix.                                        |

**Recommendation**: Prioritize **global state refactoring** first (highest impact). Then address naming, constants, and documentation. This transforms the code from fragile to maintainable.