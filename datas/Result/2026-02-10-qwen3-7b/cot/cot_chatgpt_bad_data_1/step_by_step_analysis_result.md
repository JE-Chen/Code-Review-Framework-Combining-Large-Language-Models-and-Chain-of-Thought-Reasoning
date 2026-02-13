### Code Smell Review and Fixes

---

### **1. Linter Message: `indentation-mismatch`**  
**Issue**: Loop body indentation is inconsistent.  
**Root Cause**: Mixing spaces and tabs or inconsistent indentation levels.  
**Impact**: Reduced readability and increased maintenance effort.  
**Fix**: Standardize indentation (e.g., 4 spaces or a tab).  
**Example**:  
```python
for item in items:
    process(item)
```

---

### **2. Linter Message: `unused-variable`**  
**Issue**: `results` is used but not defined.  
**Root Cause**: Variable is declared but not used.  
**Impact**: No-op logic and potential confusion.  
**Fix**: Remove or redefine the variable.  
**Example**:  
```python
# Remove
results = []
```

---

### **3. Linter Message: `missing-docstring`**  
**Issue**: `process_items` lacks a docstring.  
**Root Cause**: No explanation of function purpose.  
**Impact**: Difficulty understanding API.  
**Fix**: Add docstring.  
**Example**:  
```python
def process_items(items):
    """Process items and return results."""
    results = []
    for item in items:
        results.append(item)
    return results
```

---

### **4. Linter Message: `security-risk`**  
**Issue**: `eval` is used for arithmetic.  
**Root Cause**: Insecure operation.  
**Impact**: XSS or code injection risks.  
**Fix**: Replace with safer operations.  
**Example**:  
```python
# Replace
value = int(input("Enter value: "))
```

---

### **5. Linter Message: `cache-usage`**  
**Issue**: Cache not cleared.  
**Root Cause**: No invalidation logic.  
**Impact**: Stale data and memory leaks.  
**Fix**: Add cache invalidation.  
**Example**:  
```python
def get_data():
    cache.clear()
    return data
```

---

### **6. Linter Message: `performance-inefficiency`**  
**Issue**: `time.sleep(0.01)` is redundant.  
**Root Cause**: No performance optimization.  
**Impact**: Reduced throughput.  
**Fix**: Remove or replace with asynchronous I/O.  
**Example**:  
```python
# Remove
time.sleep(0.01)
```

---

### **7. Linter Message: `missing-exception-handling`**  
**Issue**: No error handling in `expensive_compute`.  
**Root Cause**: Unhandled exceptions.  
**Impact**: Crashes and data loss.  
**Fix**: Add try-except blocks.  
**Example**:  
```python
def expensive_compute():
    try:
        # Compute logic
    except Exception as e:
        logging.error(f"Error: {e}")
```

---

### **8. Linter Message: `redundant-code`**  
**Issue**: `get_user_data` is a wrapper.  
**Root Cause**: No value added.  
**Impact**: Redundant code.  
**Fix**: Remove or re-purpose.  
**Example**:  
```python
# Remove
def get_user_data():
    return cache.get_user()
```

---

### **Summary of Key Fixes**  
| Category | Fix | Priority |  
|---------|-----|----------|  
| Indentation | Standardize | High |  
| Unused Variables | Remove | Medium |  
| Docstrings | Add | Medium |  
| Security | Replace `eval` | High |  
| Cache | Invalidate | High |  
| Performance | Remove redundant calls | Medium |  
| Exceptions | Handle gracefully | High |  
| Redundancy | Extract logic | Medium |  

---

### **Best Practices**  
- **SOLID**: Maintainable, single responsibility.  
- **DRY**: Avoid repetition.  
- **Documentation**: Clear comments and docstrings.