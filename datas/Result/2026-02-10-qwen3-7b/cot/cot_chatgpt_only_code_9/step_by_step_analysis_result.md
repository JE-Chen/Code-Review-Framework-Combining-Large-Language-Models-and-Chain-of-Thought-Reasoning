### 📌 Code Smell Review Report with Linter Messages

---

## **1. No Unused Variables (`no-unused-vars`)**  
### **Issue**  
- `GLOBAL_CACHE` is declared but not used in any function.  
### **Root Cause**  
- Unnecessary variable declaration without purpose.  
### **Impact**  
- Reduces code clarity and increases maintenance burden.  
### **Fix**  
- Remove or comment out `GLOBAL_CACHE` if unused.  
### **Example**  
```python
# Remove unused variable
# GLOBAL_CACHE = {}
```
### **Best Practice**  
Avoid unused variables and use meaningful names.

---

## **2. Missing Docstrings (`missing-docstring`)**  
### **Issue**  
- `process_all()`, `main()`, `get_users()`, etc., lack docstrings.  
### **Root Cause**  
- Lack of documentation for public interfaces.  
### **Impact**  
- Makes code harder to understand and maintain.  
### **Fix**  
- Add docstrings explaining function purpose and parameters.  
### **Example**  
```python
def process_all():
    """Process all data from endpoints.
    Returns: Processed data.
    """
    pass
```
### **Best Practice**  
Document all public functions and classes.

---

## **3. Duplicate Code (`duplicate-code`)**  
### **Issue**  
- `get_users()`, `get_posts()`, `get_todos()` share similar logic.  
### **Root Cause**  
- Hardcoded endpoint logic and repetitive patterns.  
### **Impact**  
- Increases maintenance cost and code duplication.  
### **Fix**  
- Extract shared logic into a helper function.  
### **Example**  
```python
def fetch_data(endpoint):
    """Fetch data from specified endpoint."""
    pass
```
### **Best Practice**  
Avoid duplication and reuse common logic.

---

## **4. Poor Naming (`no-exception-handling-specific`)**  
### **Issue**  
- `fetch()` catches general exceptions without type specificity.  
### **Root Cause**  
- Lack of granular error handling.  
### **Impact**  
- Makes debugging and error recovery harder.  
### **Fix**  
- Catch specific exceptions like `ConnectionError`.  
### **Example**  
```python
try:
    response = requests.get(BASE_URL)
except ConnectionError:
    raise
```
### **Best Practice**  
Handle specific exceptions to improve robustness.

---

## **5. Code Smell Summary**  
| Category | Problem | Priority |  
|----------|---------|----------|  
| **Tight Coupling** | `APIClient` and `GLOBAL_CACHE` | High |  
| **Magic Numbers** | Hardcoded strings | Medium |  
| **Repetitive Code** | Duplicate endpoint logic | Medium |  
| **Poor Naming** | `GLOBAL_CACHE` | Medium |  
| **Unnecessary Complexity** | `main()` and helper functions | Medium |  

---

## ✅ Final Recommendations  
1. Extract `APIClient` into a utility class.  
2. Use environment variables for hardcoded strings.  
3. Refactor endpoint logic into a helper function.  
4. Rename `GLOBAL_CACHE` to `common_cache`.  
5. Simplify `main()` and separate concerns.  

--- 

This review ensures clarity, maintainability, and adherence to SOLID principles.