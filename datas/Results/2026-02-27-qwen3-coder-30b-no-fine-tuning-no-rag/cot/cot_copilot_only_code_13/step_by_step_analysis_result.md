### 1. **Global Variables Reduce Modularity and Testability**

**Issue:**  
Using global variables like `screen`, `playerX`, `enemyList`, etc., makes the code harder to test and reuse because any function can modify these values unexpectedly.

**Root Cause:**  
The code relies on shared mutable state across multiple functions instead of passing data explicitly.

**Impact:**  
This leads to tight coupling between functions, making it difficult to reason about side effects and test components in isolation.

**Fix:**  
Wrap game state inside a class (`Game`) and pass necessary data through parameters or instance attributes.

**Before:**
```python
playerX = 200
playerY = 200

def movePlayer():
    global playerX, playerY
    playerX += 5
```

**After:**
```python
class Game:
    def __init__(self):
        self.player_x = 200
        self.player_y = 200

    def move_player(self):
        self.player_x += 5
```

**Best Practice Tip:**  
Follow the *Dependency Injection* principle—pass dependencies explicitly rather than relying on global scope.

---

### 2. **Magic Numbers Should Be Replaced With Named Constants**

**Issue:**  
A magic number like `7` for enemy count is unclear and not easily maintainable.

**Root Cause:**  
Hardcoded numeric literals are used directly without meaningful labels.

**Impact:**  
It's hard to understand why `7` was chosen or to change it later without risk of breaking logic.

**Fix:**  
Define a named constant such as `ENEMY_COUNT`.

**Before:**
```python
enemyList = []
for i in range(7):
    ...
```

**After:**
```python
ENEMY_COUNT = 7
enemyList = []
for i in range(ENEMY_COUNT):
    ...
```

**Best Practice Tip:**  
Use descriptive constants instead of magic numbers for clarity and future modifications.

---

### 3. **Duplicate Code in Collision Detection**

**Issue:**  
Collision detection logic appears in more than one place, violating DRY (Don’t Repeat Yourself).

**Root Cause:**  
Same logic is repeated in different functions, increasing chances of inconsistency or bugs.

**Impact:**  
Maintaining and updating collision rules becomes error-prone and time-consuming.

**Fix:**  
Extract the collision check into a reusable helper function.

**Before:**
```python
if (playerX < e[0] + ENEMY_SIZE and
    playerX + PLAYER_SIZE > e[0] and
    playerY < e[1] + ENEMY_SIZE and
    playerY + PLAYER_SIZE > e[1]):
    # Handle collision
```

**After:**
```python
def check_collision(x1, y1, w1, h1, x2, y2, w2, h2):
    return (x1 < x2 + w2 and x1 + w1 > x2 and
            y1 < y2 + h2 and y1 + h1 > y2)

# Usage
if check_collision(playerX, playerY, PLAYER_SIZE, PLAYER_SIZE, e[0], e[1], ENEMY_SIZE, ENEMY_SIZE):
    ...
```

**Best Practice Tip:**  
Encapsulate repeated logic into helper functions or utility classes.

---

### 4. **Inconsistent Variable Naming Conventions**

**Issue:**  
Some variables use `snake_case` while others use `camelCase`.

**Root Cause:**  
Lack of consistency in naming style, possibly due to mixed development styles or lack of team guidelines.

**Impact:**  
Decreases code readability and makes it harder to follow patterns quickly.

**Fix:**  
Standardize all variable names to either `snake_case` or `camelCase`. Prefer `snake_case` for Python projects.

**Before:**
```python
playerX = 200
playerY = 200
scoreValue = 0
```

**After:**
```python
player_x = 200
player_y = 200
score_value = 0
```

**Best Practice Tip:**  
Adhere to PEP 8 naming conventions for Python code.

---

### 5. **Hardcoded Colors Make Theming Difficult**

**Issue:**  
RGB values like `(0, 255, 0)` are hardcoded in drawing functions.

**Root Cause:**  
Colors are written directly instead of being defined once and reused.

**Impact:**  
Changing themes or visual styles requires manual updates in many places.

**Fix:**  
Define named color constants at the top of the file.

**Before:**
```python
pygame.draw.rect(screen, (0, 255, 0), (playerX, playerY, PLAYER_SIZE, PLAYER_SIZE))
```

**After:**
```python
GREEN = (0, 255, 0)
RED = (255, 0, 0)

pygame.draw.rect(screen, GREEN, (playerX, playerY, PLAYER_SIZE, PLAYER_SIZE))
```

**Best Practice Tip:**  
Centralize design-related constants to support easy customization and theming.

---

### 6. **Missing Explicit Returns Can Cause Confusion**

**Issue:**  
Functions don’t always return a value explicitly, which can confuse readers or cause silent failures.

**Root Cause:**  
Inconsistent return usage, especially in conditional blocks.

**Impact:**  
Can lead to bugs where functions implicitly return `None`, causing unexpected behavior.

**Fix:**  
Ensure that every branch of a function returns something predictable.

**Before:**
```python
def update_score():
    global scoreValue
    scoreValue += 1
```

**After:**
```python
def update_score():
    global scoreValue
    scoreValue += 1
    return scoreValue
```

**Best Practice Tip:**  
Always return values from functions unless they are meant to perform side effects only.

---