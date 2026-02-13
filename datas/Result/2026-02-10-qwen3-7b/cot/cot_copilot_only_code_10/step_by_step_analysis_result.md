### **Code Smell Review & Analysis**

---

### **1. Missing Docstrings (High)**  
**Problem Location**: Class and function docstrings are missing.  
**Root Cause**: Lack of documentation for clarity and maintainability.  
**Impact**: Hard to understand purpose, increase learning curve.  
**Fix**: Add docstrings with purpose, parameters, and examples.  
**Example**:  
```python
class APIClient:
    """Fetch data from API endpoints."""
    def fetch(self, url):
        """Fetch data from a URL."""
        ...
```
**Best Practice**: Use docstrings for clarity and maintainability.  

---

### **2. Unhandled Exceptions (Medium)**  
**Problem Location**: `fetch()` method has no exception handling.  
**Root Cause**: Errors are silently ignored.  
**Impact**: Bugs are hard to trace and fix.  
**Fix**: Wrap in `try/except` and log errors.  
**Example**:  
```python
def fetch(self, url):
    try:
        ...  # Fetch logic
    except Exception as e:
        logger.error(f"Fetch failed: {e}")
```
**Best Practice**: Handle errors explicitly and log them.  

---

### **3. Global State Management (High)**  
**Problem Location**: `GLOBAL_CACHE` is used but not declared.  
**Root Cause**: Global variable not encapsulated.  
**Impact**: Hard to clean up and maintain.  
**Fix**: Declare as class-level variable and add `clear_cache()`.  
**Example**:  
```python
class APIClient:
    GLOBAL_CACHE = {}
    def clear_cache(self):
        del GLOBAL_CACHE
```
**Best Practice**: Encapsulate global state in classes.  

---

### **4. No Conditional Logic (Medium)**  
**Problem Location**: `process_all()` lacks comments for logic.  
**Root Cause**: Conditional logic is unclear.  
**Impact**: Hard to maintain or debug.  
**Fix**: Add comments explaining logic flow.  
**Example**:  
```python
if data:
    process(data)
else:
    logger.warning("No data to process")
```
**Best Practice**: Document logic for readability.  

---

### **Summary of Code Smells**  
| Category | Issue | Fix | Priority |  
|----------|-------|-----|----------|  
| Docstrings | Missing | Add | High |  
| Exceptions | Unhandled | Wrap | Medium |  
| Global State | Unused | Encapsulate | High |  
| Comments | Missing | Add | Medium |  
| Logic | Unclear | Document | Medium |  

---

### **Final Recommendations**  
1. Use docstrings for all methods.  
2. Implement try/except blocks for error handling.  
3. Encapsulate global state in classes.  
4. Add comments for logic and edge cases.  
5. Extract shared logic into reusable methods.