### **Code Smell & Linter Analysis Summary**

---

### **1. Missing Docstrings**  
**Issue**: Functions and classes lack docstrings.  
**Root Cause**: Lack of documentation for clarity and maintainability.  
**Impact**: Developers struggle to understand purpose, parameters, and usage.  
**Fix**: Add docstrings with examples.  
**Example**:  
```python
def get_users():
    """Retrieve user data from API.
    Args: None
    Returns: List of users.
    """
```

---

### **2. Code Duplication**  
**Issue**: `get_users()`, `get_posts()`, `get_comments()` share identical logic.  
**Root Cause**: Hardcoded logic and repeated boilerplate.  
**Impact**: Hard to maintain and update.  
**Fix**: Extract shared logic into a utility function.  
**Example**:  
```python
def _common_request(url, headers):
    """Common request handling logic."""
```

---

### **3. Improper Error Handling**  
**Issue**: Errors are printed but not returned or logged.  
**Root Cause**: Lack of structured error propagation.  
**Impact**: Hard to debug and handle exceptions.  
**Fix**: Return error codes or log with context.  
**Example**:  
```python
try:
    result = process_data(data)
except Exception as e:
    logging.error(f"Error: {e}")
```

---

### **4. Inconsistent Logic**  
**Issue**: `process_data()` handles multiple tasks in a single block.  
**Root Cause**: Reduced readability and testability.  
**Impact**: Hard to maintain and debug.  
**Fix**: Split into smaller, focused functions.  
**Example**:  
```python
def filter_users(data):
    """Filter users based on criteria."""
def log_results(data):
    """Log processed results."""
```

---

### **5. Inefficient Output**  
**Issue**: `main()` prints results with conditional checks.  
**Root Cause**: Redundant code and lack of abstraction.  
**Impact**: Reduced maintainability.  
**Fix**: Refactor output into a helper function.  
**Example**:  
```python
def output_results(processed_data):
    """Format and print results."""
```

---

### **6. Best Practices**  
- **SOLID**: Encapsulate responsibilities (e.g., `process_data()` for filtering).  
- **DRY**: Avoid repetition (e.g., shared logic in `_common_request`).  
- **Naming**: Use descriptive names (e.g., `processed_results` instead of `GLOBAL_RESULTS`).  

---

### **Summary of Key Fixes**  
| Priority | Fix | Example |  
|---------|-----|---------|  
| High | Extract shared logic | `_common_request()` |  
| Medium | Add docstrings | `get_users()` |  
| Medium | Log errors | `try-except` block |