### 📌 Code Smell & Linter Analysis

---

#### **1. Linter Message: `no-early-return`**  
**Problem**: `movePlayer()` returns early without handling all conditions.  
**Root Cause**: Poorly structured logic with premature returns.  
**Impact**: Bugs, unclear behavior, and difficulty testing.  
**Fix**: Use `if-else` or `return` after all conditions.  
**Example**:  
```python
if keys[pygame.K_LEFT]: vx = -SPEED
if keys[pygame.K_RIGHT]: vx = SPEED
if keys[pygame.K_UP]: vy = -SPEED
return
```  
**Best Practice**: Maintain logical flow with explicit return points.  

---

#### **2. Linter Message: `no-global-variable`**  
**Problem**: `screen` is declared globally in `initGame()`.  
**Root Cause**: Lack of encapsulation and parameter passing.  
**Impact**: Hard to test and maintain.  
**Fix**: Pass `screen` as a parameter to `initGame()`.  
**Example**:  
```python
def initGame(screen):
    # Use screen instead of global
```  
**Best Practice**: Avoid global variables and pass dependencies.  

---

#### **3. Linter Message: `no-unnecessary-logic`**  
**Problem**: `checkCollision()` modifies enemy positions instead of removing them.  
**Root Cause**: Poor game state handling.  
**Impact**: Game state inconsistencies.  
**Fix**: Reset or remove enemies.  
**Example**:  
```python
if enemy.x < 0:
    enemy.x = SCREEN_WIDTH
    enemy.y = random.randint(0, SCREEN_HEIGHT)
```  
**Best Practice**: Enforce game state rules explicitly.  

---

#### **4. Linter Message: `no-unnecessary-variable`**  
**Problem**: `scoreValue` is incremented but not reset.  
**Root Cause**: Missing logic to clean up state.  
**Impact**: Score not accurate.  
**Fix**: Reset `scoreValue` on enemy removal.  
**Example**:  
```python
if enemy.isRemoved:
    scoreValue = 0
```  
**Best Practice**: Clean up state variables explicitly.  

---

### 📊 Code Smell Summary & Fixes

---

#### **1. Long Function (`mainLoop()`)**
- **Problem**: Centralized game logic.  
- **Fix**: Split into smaller functions (e.g., `handleEvents()`, `updateGame()`, `renderFrame()`).  
- **Best Practice**: Apply *SOLID* principles.  

---

#### **2. Magic Numbers**  
- **Problem**: Constants like `SPEED` are hardcoded.  
- **Fix**: Define constants in a module.  
- **Best Practice**: Use constants for game properties.  

---

#### **3. Duplicate Code**  
- **Problem**: Shared initialization logic.  
- **Fix**: Extract into helper functions.  
- **Best Practice**: Avoid code duplication.  

---

#### **4. Unclear Naming**  
- **Problem**: Variables like `scoreValue` are generic.  
- **Fix**: Use descriptive names.  
- **Best Practice**: Follow *Naming Conventions* (e.g., `playerScore`).  

---

#### **5. Tight Coupling**  
- **Problem**: `mainLoop()` handles too many responsibilities.  
- **Fix**: Use event-driven architecture or separate layers.  
- **Best Practice**: Follow *Single Responsibility Principle*.  

---

### 💡 Root Cause & General Patterns
- **Common Patterns**: Premature returns, global variables, and lack of encapsulation.  
- **Key Principle**: *SOLID* and *DRY* principles reduce complexity.  

---

### ✅ Final Recommendation
Break down logic into smaller functions, define constants, and enforce encapsulation. Use descriptive names and avoid global variables.