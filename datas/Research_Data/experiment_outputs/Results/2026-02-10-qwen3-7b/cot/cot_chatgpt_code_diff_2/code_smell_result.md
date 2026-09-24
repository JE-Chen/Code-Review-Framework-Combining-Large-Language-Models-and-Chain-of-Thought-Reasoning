### Code Smell Review

---

### **1. Code Smell Type**: Magic Numbers & Inconsistent Naming  
**Problem Location**: `STATE["velocity"] = 3`, `delta = now - STATE["last_time"]`, and `STATE["score"] += int(delta * 10) % 7`  
**Detailed Explanation**:  
- `3` and `7` are hardcoded and lack context.  
- `STATE["score"]` is calculated with a non-descriptive formula.  
- Variable names like `STATE` and `delta` are ambiguous.  

**Improvement Suggestions**:  
1. Replace hardcoded values with configurable constants.  
2. Rename `STATE` to `game_state` and `delta` to `time_delta`.  
3. Add comments explaining the score calculation logic.  

**Priority Level**: High  

---

### **2. Code Smell Type**: Poorly Encapsulated Game State  
**Problem Location**: Global `STATE` dictionary and lack of class-based design  
**Detailed Explanation**:  
- `STATE` is a global variable, making it hard to test or modify.  
- No encapsulation of game logic into classes (e.g., `Game`, `Player`).  

**Improvement Suggestions**:  
1. Create a `Game` class to encapsulate `STATE` and game logic.  
2. Extract methods like `do_everything()` and `move_player()` into helper functions.  

**Priority Level**: Medium  

---

### **3. Code Smell Type**: Inconsistent Formatting & Comments  
**Problem Location**: Mixed indentation, missing comments for complex logic  
**Detailed Explanation**:  
- Indentation inconsistencies (e.g., `if` blocks with mixed spaces).  
- Missing comments for critical logic (e.g., score calculation).  

**Improvement Suggestions**:  
1. Standardize indentation (e.g., 4 spaces).  
2. Add inline comments for complex calculations (e.g., `delta * 10 % 7`).  

**Priority Level**: Low  

---

### **4. Code Smell Type**: Missing Boundary Conditions  
**Problem Location**: Unhandled edge cases (e.g., player position out of bounds)  
**Detailed Explanation**:  
- The player’s position is not clamped to screen boundaries in `move_player()`.  
- No validation for input keys (e.g., invalid key presses).  

**Improvement Suggestions**:  
1. Add clamping for player position in `move_player()`.  
2. Validate key presses and handle invalid inputs.  

**Priority Level**: Medium  

---

### **5. Code Smell Type**: Redundant Logic in `draw_stuff()`  
**Problem Location**: Overlapping logic between `draw_stuff()` and `do_everything()`  
**Detailed Explanation**:  
- `draw_stuff()` and `do_everything()` share similar operations (e.g., color updates).  

**Improvement Suggestions**:  
1. Move color updates to a separate function (e.g., `update_colors()`).  
2. Extract drawing logic into a reusable function.  

**Priority Level**: Medium  

---

### **6. Code Smell Type**: No Unit Tests  
**Problem Location**: No test cases for critical functions  
**Detailed Explanation**:  
- No tests for game state transitions or player movement.  

**Improvement Suggestions**:  
1. Add unit tests for `do_everything()`, `move_player()`, and `draw_stuff()`.  
2. Use a testing framework (e.g., `unittest` or `pytest`).  

**Priority Level**: Low  

---

### **Summary of Fixes & Recommendations**  
| Smell Type | Recommendation | Priority |  
|------------|------------------|----------|  
| Magic Numbers | Replace with constants | High |  
| Poorly Encapsulated State | Use classes | Medium |  
| Inconsistent Formatting | Add comments | Low |  
| Missing Boundary Checks | Add clamping | Medium |  
| Redundant Logic | Extract functions | Medium |  
| No Tests | Add unit tests | Low |