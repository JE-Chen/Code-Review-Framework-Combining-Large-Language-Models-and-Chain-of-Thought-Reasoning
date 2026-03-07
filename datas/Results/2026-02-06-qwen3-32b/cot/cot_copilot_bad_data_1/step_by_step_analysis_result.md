### Code Quality Review: Linter Messages Analysis

---

#### **1. Mutable Default Argument**  
**Issue**:  
Mutable default arguments (e.g., `container=[]`) persist across function calls, causing unintended shared state.  
**Root Cause**:  
Default arguments are initialized *once* at function definition, not per call. Subsequent calls reuse the same mutable object.  
**Impact**:  
High risk of subtle bugs (e.g., accumulated values across calls). Breaks predictable function behavior.  
**Fix**:  
Use `None` as the default and initialize inside the function.  
```python
# Before (buggy)
def add_item(item, container=[]):
    container.append(item)
    return container

# After (fixed)
def add_item(item, container=None):
    if container is None:
        container = []
    container.append(item)
    return container
```  
**Best Practice**:  
*Never use mutable objects as default arguments.* Always initialize inside the function.

---

#### **2. Global Mutable Variable**  
**Issue**:  
Mutating a global variable (`shared_list`) creates hidden dependencies and complicates testing.  
**Root Cause**:  
Global state couples unrelated logic, making functions non-deterministic and hard to isolate.  
**Impact**:  
High risk of unintended side effects and brittle tests. Violates separation of concerns.  
**Fix**:  
Pass state explicitly instead of relying on globals.  
```python
# Before (bad)
shared_list = []
def append_global(value):
    shared_list.append(value)

# After (good)
def append_global(container, value):
    container.append(value)
    return container
```  
**Best Practice**:  
*Prefer dependency injection over global state.* Isolate state within functions.

---

#### **3. Input Mutation Without Documentation**  
**Issue**:  
Function mutates input (`data`) without documentation, violating caller expectations.  
**Root Cause**:  
Assuming inputs are immutable without explicit contracts.  
**Impact**:  
Hard-to-debug bugs (e.g., callers relying on unmodified data).  
**Fix**:  
Return a new list instead of mutating the input.  
```python
# Before (buggy)
def mutate_input(data):
    for i in range(len(data)):
        data[i] *= 2  # Mutates input!

# After (safe)
def double_list(values):
    return [v * 2 for v in values]  # Returns new list
```  
**Best Practice**:  
*Prefer immutability.* Document mutation explicitly if unavoidable.

---

#### **4. Broad Exception Handling**  
**Issue**:  
Catching `Exception` masks critical errors (e.g., `KeyboardInterrupt`).  
**Root Cause**:  
Overly generic exception handling ignores edge cases.  
**Impact**:  
Silent failures could lead to data corruption or crashes.  
**Fix**:  
Catch specific exceptions.  
```python
# Before (dangerous)
try:
    result = a / b
except Exception:
    return None

# After (secure)
try:
    return a / b
except ZeroDivisionError:
    return None
```  
**Best Practice**:  
*Catch only expected exceptions.* Never swallow all errors.

---

#### **5. Inconsistent Return Types**  
**Issue**:  
Function returns `int` or `str` inconsistently (e.g., `42` vs `"forty-two"`).  
**Root Cause**:  
No clear return contract.  
**Impact**:  
Callers must handle multiple types, risking `TypeError` (e.g., `42 + "text"`).  
**Fix**:  
Standardize return types.  
```python
# Before (unsafe)
def inconsistent_return(flag):
    if flag: return 42
    else: return "forty-two"

# After (consistent)
def consistent_return(flag):
    return "42" if flag else "forty-two"  # Always string
```  
**Best Practice**:  
*Functions should return a single type.* Avoid type gymnastics.

---

#### **6. Repeated Computation**  
**Issue**:  
`len(values)` recalculated in every loop iteration.  
**Root Cause**:  
Failure to cache expensive operations.  
**Impact**:  
Wasted CPU cycles (especially for large lists).  
**Fix**:  
Precompute length once.  
```python
# Before (inefficient)
for i in range(len(values)):
    # ... 

# After (efficient)
n = len(values)
for i in range(n):
    # ...
```  
**Best Practice**:  
*Cache repeated computations.* Optimize loops early.

---

#### **7. Side Effect in List Comprehension**  
**Issue**:  
Using list comprehensions for side effects (e.g., `print`), not for building collections.  
**Root Cause**:  
Misusing comprehensions as loops.  
**Impact**:  
Confuses readers and violates Python idioms.  
**Fix**:  
Use explicit loops for side effects.  
```python
# Before (anti-pattern)
[print(i) for i in range(3)]  # Returns [None, None, None]!

# After (clear)
for i in range(3):
    print(i)
```  
**Best Practice**:  
*Comprehensions build lists; loops handle side effects.*

---

#### **8. Unsafe `eval()` Usage**  
**Issue**:  
`eval()` executes arbitrary code, enabling remote code execution (RCE) attacks.  
**Root Cause**:  
Using `eval()` on untrusted input.  
**Impact**:  
Critical security vulnerability (e.g., attackers inject malicious code).  
**Fix**:  
Replace with safe alternatives like `ast.literal_eval`.  
```python
# Before (dangerous)
def run_code(code_str):
    return eval(code_str)  # Executes any code!

# After (secure)
import ast
def run_code_safe(code_str):
    return ast.literal_eval(code_str)  # Only safe for literals
```  
**Best Practice**:  
*Never use `eval()` on user input.* Prefer safe parsing methods.