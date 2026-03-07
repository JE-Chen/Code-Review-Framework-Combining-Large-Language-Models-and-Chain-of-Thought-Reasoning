### Code Smell Type: I/O Operations in Business Logic  
**Problem Location**:  
```python
def process_user_input(user_input):
    if not isinstance(user_input, str):
        print("Invalid input!")  # I/O
        return None
    if "admin" in user_input:
        print("Access granted")  # I/O
        return True
    else:
        print("Access denied")  # I/O
        return False
```  
**Detailed Explanation**:  
The function mixes business logic (input validation, access control) with side-effecting I/O operations (`print`). This violates the **Single Responsibility Principle** and makes the function:  
- Untestable (cannot verify logic without capturing stdout)  
- Inflexible (caller cannot customize output)  
- Error-prone (unexpected I/O may occur during testing)  
RAG rules explicitly prohibit this: *"Functions and methods should have a single, clear responsibility."*  

**Improvement Suggestions**:  
1. Remove I/O operations and return pure data:  
```python
def process_user_input(user_input):
    if not isinstance(user_input, str):
        return {"status": "error", "message": "Invalid input"}
    return {"status": "granted" if "admin" in user_input else "denied"}
```  
2. Move I/O to a separate presentation layer (e.g., CLI handler).  
**Priority Level**: High  

---

### Code Smell Type: Global State Dependency  
**Problem Location**:  
```python
hidden_flag = True
def secret_behavior(x):
    if hidden_flag:  # Global dependency
        return x * 2
    else:
        return x + 2
```  
**Detailed Explanation**:  
The function `secret_behavior` relies on the global variable `hidden_flag`, violating:  
- **Predictability**: Behavior changes without explicit input  
- **Testability**: Requires global state setup to test  
- **Maintainability**: Hidden coupling makes code harder to refactor  
RAG rule: *"Avoid functions whose behavior changes based on hidden flags, global variables, or implicit context."*  

**Improvement Suggestions**:  
1. Pass state explicitly:  
```python
def secret_behavior(x, use_double=False):
    return x * 2 if use_double else x + 2
```  
2. Replace global with dependency injection (e.g., via class).  
**Priority Level**: High  

---

### Code Smell Type: Implicit Truthiness Check  
**Problem Location**:  
```python
def check_value(val):
    if val:  # Implicit truthiness
        return "Has value"
    else:
        return "No value"
```  
**Detailed Explanation**:  
The condition `if val:` is ambiguous:  
- Returns "Has value" for truthy values like `0` (if `val` is `0` in some contexts)  
- Returns "No value" for falsy values like `""`, `[]`, `None`  
RAG rule: *"Do not rely on implicit truthiness for complex objects or return values."*  
This risks subtle bugs (e.g., `check_value(0)` returns "Has value" in some frameworks).  

**Improvement Suggestions**:  
1. Explicitly check for `None` or empty values:  
```python
def check_value(val):
    return "Has value" if val is not None and val != "" else "No value"
```  
2. Use type-specific checks (e.g., `if isinstance(val, str) and val.strip()`).  
**Priority Level**: Medium  

---

### Code Smell Type: Non-Descriptive Function Name  
**Problem Location**:  
```python
def f(x):
    return x * 7 + 13
```  
**Detailed Explanation**:  
The name `f` is meaningless and violates naming conventions:  
- Fails to convey intent ("Why 7 and 13?")  
- Hinders readability and maintainability  
RAG rule: *"Prefer clear and descriptive variable and function names over short or ambiguous ones."*  

**Improvement Suggestions**:  
1. Rename to reflect purpose (e.g., `calculate_discount` if applicable):  
```python
def calculate_discount(price):
    return price * 0.7 + 13  # Example: 30% off + $13 fixed
```  
**Priority Level**: Low  

---

### Code Smell Type: Time-Dependent Logic Without Abstraction  
**Problem Location**:  
```python
import time
def timestamped_message(msg):
    return f"{time.time()} - {msg}"  # Uses system time
```  
**Detailed Explanation**:  
The function depends on `time.time()`, making it:  
- Non-deterministic (fails in unit tests)  
- Hard to mock for testing  
RAG rule: *"Be careful with time-dependent logic without proper abstraction."*  

**Improvement Suggestions**:  
1. Inject time source:  
```python
def timestamped_message(msg, time_source=time.time):
    return f"{time_source()} - {msg}"
```  
2. Use dependency injection in tests (e.g., mock `time_source`).  
**Priority Level**: Medium  

---

### Code Smell Type: Dangerous `eval` Usage  
**Problem Location**:  
```python
def unsafe_eval(user_code):
    return eval(user_code)  # Security risk
```  
**Detailed Explanation**:  
`eval` executes arbitrary code, introducing:  
- **Critical security vulnerability** (e.g., remote code execution)  
- **Unpredictable behavior** (depends on user input)  
RAG rule: *"Avoid using `eval`, `exec`, or dynamic code execution unless there is a strong justification."*  

**Improvement Suggestions**:  
1. Replace with safe alternatives (e.g., `ast.literal_eval` for JSON-like data):  
```python
import ast
def safe_eval(user_code):
    try:
        return ast.literal_eval(user_code)
    except (SyntaxError, ValueError):
        raise ValueError("Invalid expression")
```  
**Priority Level**: High  

---

### Code Smell Type: Input Mutation Without Documentation  
**Problem Location**:  
```python
def risky_update(data):
    try:
        data["count"] += 1  # Mutates input
    except Exception:
        data["count"] = 0
    return data
```  
**Detailed Explanation**:  
- **Side effect**: Modifies caller’s `data` dictionary  
- **Poor error handling**: Catches all exceptions (including `KeyError`)  
- **Undocumented**: Caller unaware of mutation  
RAG rules: *"Avoid modifying input arguments unless documented"* and *"Prefer explicit parameters over hidden state."*  

**Improvement Suggestions**:  
1. Return a new dictionary instead of mutating:  
```python
def risky_update(data):
    updated = data.copy()
    try:
        updated["count"] += 1
    except KeyError:
        updated["count"] = 0
    return updated
```  
2. Use explicit error types (e.g., `KeyError` instead of `Exception`).  
**Priority Level**: Medium  

---

### Summary of Priority Levels  
| Code Smell Type                     | Priority |
|-------------------------------------|----------|
| I/O in Business Logic               | High     |
| Global State Dependency             | High     |
| Implicit Truthiness Check           | Medium   |
| Time-Dependent Logic                | Medium   |
| Dangerous `eval` Usage              | High     |
| Input Mutation Without Documentation| Medium   |
| Non-Descriptive Function Name       | Low      |