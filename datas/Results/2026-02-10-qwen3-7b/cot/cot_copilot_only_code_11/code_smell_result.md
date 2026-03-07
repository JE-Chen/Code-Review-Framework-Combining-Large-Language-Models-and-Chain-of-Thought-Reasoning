### Code Smell Review

---

#### **1. Code Smell Type**: Long Function
**Problem Location**: `calculate_average_scores()` and `filter_high_scores()`  
**Detailed Explanation**:  
- Both functions contain complex logic and are tightly coupled with the `DATA` dictionary.  
- Lack of encapsulation and separation of concerns reduces readability and testability.  
- Potential for bugs and maintenance challenges.  

**Improvement Suggestions**:  
- Split into smaller, focused functions.  
- Extract common logic into helper methods.  

**Priority Level**: High  

---

#### **2. Code Smell Type**: Magic Numbers
**Problem Location**: `DATA["config"]["threshold"] = 50`  
**Detailed Explanation**:  
- The threshold value is hardcoded and not documented.  
- Makes the code fragile to changes and harder to understand.  

**Improvement Suggestions**:  
- Define the threshold in a constant or configuration file.  
- Add documentation for its purpose.  

**Priority Level**: Medium  

---

#### **3. Code Smell Type**: Duplicate Code
**Problem Location**: `main()` and `process_misc()`  
**Detailed Explanation**:  
- The `main()` function prints results, and `process_misc()` does similar logic.  
- Repetitive code increases maintenance effort.  

**Improvement Suggestions**:  
- Extract common logic into a helper function.  
- Use a single print statement or formatter.  

**Priority Level**: Medium  

---

#### **4. Code Smell Type**: Unclear Naming
**Problem Location**: `total`, `avg`, `high_scores`, `result`  
**Detailed Explanation**:  
- Variable names are generic and lack clarity.  
- Makes it hard to understand the purpose of each variable.  

**Improvement Suggestions**:  
- Use descriptive names like `user_scores_total` or `score_avg`.  

**Priority Level**: Medium  

---

#### **5. Code Smell Type**: Tight Coupling
**Problem Location**: `main()` and `DATA`  
**Detailed Explanation**:  
- Functions rely on global `DATA` and hardcoded values.  
- Makes the code brittle and harder to refactor.  

**Improvement Suggestions**:  
- Encapsulate data and logic in classes or modules.  
- Use dependency injection.  

**Priority Level**: High  

---

#### **6. Code Smell Type**: Violation of Single Responsibility Principle
**Problem Location**: `process_misc()`  
**Detailed Explanation**:  
- Handles data processing and conditional logic in one function.  
- Makes the function too complex and hard to maintain.  

**Improvement Suggestions**:  
- Split into smaller, focused functions.  
- Extract common logic into helper methods.  

**Priority Level**: High  

---

### Summary of Key Issues
| Smell Type | Priority | Impact |
|------------|----------|--------|
| Long Function | High | Reduces readability and testability |
| Magic Numbers | Medium | Hardens maintenance and understanding |
| Duplicate Code | Medium | Increases maintenance effort |
| Unclear Naming | Medium | Hinders comprehension |
| Tight Coupling | High | Increases fragility and complexity |
| Violation of Single Responsibility | High | Makes code harder to maintain |

---

### Recommended Refactor
- Extract helper functions for averaging, filtering, and data processing.  
- Use constants for thresholds and flags.  
- Encapsulate data and logic in classes.