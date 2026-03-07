### 1. **Global Variables Usage**
**Issue:**  
The code relies heavily on global variables (`screen`, `playerX`, `playerY`, etc.), reducing modularity and testability.

**Explanation:**  
When functions depend on global state, they become tightly coupled and harder to isolate for testing or reuse.

**Impact:**  
Makes debugging difficult and increases risk of unintended side effects.

**Fix Suggestion:**  
Encapsulate game state into a class so that all related data and behavior are grouped together.

```python
class Game:
    def __init__(self):
        self.screen = ...
        self.player_x = ...
        self.player_y = ...
        # other fields
```

**Best Practice Tip:**  
Follow encapsulation principles by bundling related data and methods into classes.

---

### 2. **Magic Numbers**
**Issue:**  
Hardcoded values like `640`, `480`, `9`, and `27` make the code less readable and flexible.

**Explanation:**  
These numbers lack meaning unless explained elsewhere, which hurts understanding and future modifications.

**Impact:**  
Code becomes brittle and harder to adapt if dimensions or counts change.

**Fix Suggestion:**  
Define constants with descriptive names:

```python
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
ENEMY_COUNT = 9
FPS = 27
```

**Best Practice Tip:**  
Always prefer named constants over raw numbers.

---

### 3. **Hardcoded Loop Count**
**Issue:**  
A loop uses a hardcoded number (`9`) to determine how many enemies to spawn.

**Explanation:**  
This makes it hard to adjust enemy count without changing core logic.

**Impact:**  
Limits extensibility and readability.

**Fix Suggestion:**  
Use a constant instead:

```python
for i in range(ENEMY_COUNT):
```

**Best Practice Tip:**  
Avoid magic numbers in control structures.

---

### 4. **Inconsistent Naming Conventions**
**Issue:**  
Variable names mix snake_case and camelCase styles (`playerX`, `enemyList`).

**Explanation:**  
Python follows PEP 8, which recommends snake_case for identifiers.

**Impact:**  
Confusing and inconsistent style impacts readability.

**Fix Suggestion:**  
Rename variables consistently using snake_case:

```python
player_x = ...
enemy_list = ...
score_value = ...
```

**Best Practice Tip:**  
Stick to one naming convention throughout your project.

---

### 5. **Inline Logic**
**Issue:**  
Collision detection logic is embedded directly in a function.

**Explanation:**  
Mixes unrelated responsibilities within one function.

**Impact:**  
Harder to test or refactor independently.

**Fix Suggestion:**  
Extract logic into dedicated helper functions:

```python
def detect_collision(player_rect, enemy_rect):
    return player_rect.colliderect(enemy_rect)

def update_score(score):
    return score + 1
```

**Best Practice Tip:**  
Each function should have a single purpose.

---

### 6. **Tight Coupling**
**Issue:**  
Drawing and updating logic depend on global variables rather than being passed data explicitly.

**Explanation:**  
Functions cannot be reused without knowing their dependencies.

**Impact:**  
Decreases flexibility and reusability.

**Fix Suggestion:**  
Pass required state as arguments:

```python
def draw_everything(screen, player_pos, enemies, score):
    ...
```

**Best Practice Tip:**  
Design functions with minimal side effects and explicit input/output contracts.

---

### 7. **Implicit State Change**
**Issue:**  
Modifying global enemy positions inside loops may cause unpredictable results.

**Explanation:**  
Mutating shared mutable state during iteration leads to race-like behaviors.

**Impact:**  
Can produce incorrect game state or bugs that are hard to trace.

**Fix Suggestion:**  
Avoid modifying shared data during iteration. Prefer creating new arrays or copying data before modification.

**Best Practice Tip:**  
Never mutate collections you're iterating over unless carefully handled.

---

### 8. **Unused Import**
**Issue:**  
The module `sys` is imported but never used.

**Explanation:**  
Cluttered import statements add noise and suggest outdated code.

**Impact:**  
Minor inconvenience but reflects poor hygiene.

**Fix Suggestion:**  
Remove unused imports:

```python
# Remove this line if not needed:
import sys
```

**Best Practice Tip:**  
Keep imports clean and relevant only when used.

---

### 9. **Long Function**
**Issue:**  
The `movePlayer()` function combines input handling and movement logic.

**Explanation:**  
Too much work in one function breaks SRP.

**Impact:**  
Difficult to read, debug, or extend.

**Fix Suggestion:**  
Split into smaller functions:

```python
def handle_input():
    ...

def update_position():
    ...

def clamp_position():
    ...
```

**Best Practice Tip:**  
Keep functions focused on a single responsibility.

---

### 10. **Violation of Single Responsibility Principle**
**Issue:**  
`checkCollision()` does multiple things — check, score, respawn.

**Explanation:**  
Complexity grows with combined logic.

**Impact:**  
Testing and maintaining this function becomes challenging.

**Fix Suggestion:**  
Separate concerns:

```python
def detect_collision():
    ...

def update_score():
    ...

def respawn_enemy():
    ...
```

**Best Practice Tip:**  
One function, one job.

---

### 11. **Lack of Input Validation**
**Issue:**  
No checks for invalid positions or edge cases.

**Explanation:**  
Can lead to visual artifacts or crashes due to bad data.

**Impact:**  
Unstable user experience.

**Fix Suggestion:**  
Validate inputs early:

```python
if x < 0 or x > SCREEN_WIDTH:
    raise ValueError("Invalid position")
```

**Best Practice Tip:**  
Assume nothing; validate assumptions early.

---

### 12. **Poor Exception Handling**
**Issue:**  
No error handling for critical operations like Pygame initialization.

**Explanation:**  
Silent failures or ungraceful exits degrade usability.

**Impact:**  
Hard to diagnose runtime problems.

**Fix Suggestion:**  
Wrap essential sections:

```python
try:
    pygame.init()
except Exception as e:
    print(f"Failed to initialize Pygame: {e}")
```

**Best Practice Tip:**  
Log meaningful errors instead of letting them crash silently.

---

### 13. **Hardcoded Font Size**
**Issue:**  
Font rendering is tightly coupled to fixed-size text.

**Explanation:**  
Layout-sensitive code is fragile.

**Impact:**  
Visual inconsistencies across different environments.

**Fix Suggestion:**  
Use scalable layouts or dynamic font sizing.

**Best Practice Tip:**  
Make rendering logic responsive to environment changes.

---