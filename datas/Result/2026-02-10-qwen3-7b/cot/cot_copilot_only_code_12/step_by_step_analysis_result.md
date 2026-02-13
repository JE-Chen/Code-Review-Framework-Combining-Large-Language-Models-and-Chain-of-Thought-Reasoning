### Code Smell Analysis

---

### **1. No Global Variable Usage**  
**Issue**: Global variables `DATAFRAME` and `tempStorage` are declared but not used in the function logic.  
**Root Cause**: Lack of encapsulation and visibility. Functions rely on global state instead of local parameters.  
**Impact**: Hard to test, maintain, or debug.  
**Fix**: Localize variables within function scope.  
**Example**:  
```python
def calculate_statistics(data):
    meanA = data['A'].mean()
    meanB = data['B'].mean()
    return meanA, meanB
```
**Best Practice**: Use parameters or local variables instead of global state.  

---

### **2. Vague Function Name**  
**Issue**: Function `calcStats()` lacks semantic clarity.  
**Root Cause**: Name is too generic and doesn't reflect purpose.  
**Impact**: Poor readability and maintenance.  
**Fix**: Rename to `calculate_statistics()` or `compute_statistics()`.  
**Best Practice**: Use descriptive names aligned with function logic.  

---

### **3. Duplicated Logic in `calcStats()`**  
**Issue**: Mean calculations for "A" and "B" are repeated.  
**Root Cause**: Shared logic in a single function.  
**Impact**: Increased code duplication and reduced maintainability.  
**Fix**: Extract common logic into a helper function.  
**Example**:  
```python
def _calculate_mean(df, column):
    return df[column].mean()

def calculate_statistics(df):
    return {_calculate_mean(df, 'A'), _calculate_mean(df, 'B')}
```
**Best Practice**: Extract shared logic into reusable helper functions.  

---

### **4. Unused Variable `tempStorage`**  
**Issue**: Variable is declared but never used.  
**Root Cause**: Unused variables consume memory and clutter code.  
**Impact**: Memory leaks and reduced clarity.  
**Fix**: Remove or clear `tempStorage`.  
**Best Practice**: Eliminate unused variables and parameters.  

---

### **5. Missing Docstring**  
**Issue**: No documentation for `calcStats()` or `main()`.  
**Root Cause**: Lack of comments or explanations.  
**Impact**: Hard to understand the code’s purpose.  
**Fix**: Add inline comments or docstrings.  
**Example**:  
```python
def calculate_statistics(data):
    """Calculate mean values for columns A and B."""
    return meanA, meanB
```
**Best Practice**: Use docstrings to explain function purpose and logic.  

---

### **6. Missing Unit Tests**  
**Issue**: No tests for `loadData()`, `calcStats()`, or `plotData()`.  
**Root Cause**: Lack of automated testing.  
**Impact**: Uncertainty about correctness and reliability.  
**Fix**: Add test cases for edge scenarios.  
**Best Practice**: Write tests to ensure functionality and correctness.  

---

### **Summary of Key Fixes**  
| Issue | Fix | Priority |  
|------|-----|----------|  
| Global variables | Localize variables | High |  
| Vague function name | Rename and document | Medium |  
| Duplicated code | Extract helper functions | Medium |  
| Unused variables | Remove or clear | Medium |  
| No docstrings | Add comments/docstrings | Medium |  
| No tests | Add unit tests | Low |  

---

### **Final Best Practice Note**  
Use **SOLID principles** (Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, Dependency Inversion) to structure code, reduce coupling, and improve maintainability.