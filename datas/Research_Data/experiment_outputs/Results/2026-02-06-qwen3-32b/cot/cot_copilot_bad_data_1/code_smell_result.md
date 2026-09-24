### Code Smell Type: Mutable Default Argument
**Problem Location:**  
`def add_item(item, container=[]):`  
**Detailed Explanation:**  
The mutable default argument `container=[]` is initialized only once at function definition time. Subsequent calls without an explicit `container` argument share the same list instance, leading to unexpected persistent state. For example, `add_item(1)` followed by `add_item(2)` returns `[1, 2]` instead of `[1]` and `[2]` as intended. This violates the principle of predictable function behavior and causes subtle bugs.  
**Improvement Suggestions:**  
Replace with `container=None` and initialize inside the function:  
```python
def add_item(item, container=None):
    if container is None:
        container = []
    container.append(item)
    return container
```  
**Priority Level:** High  

---

### Code Smell Type: Global State Mutation
**Problem Location:**  
`shared_list.append(value)` in `append_global(value)`  
**Detailed Explanation:**  
The function mutates a global variable (`shared_list`), creating hidden coupling. This makes the function non-deterministic (behavior depends on external state), hard to test in isolation, and prone to unintended side effects. For example, unrelated code modifying `shared_list` could break `append_global`'s logic.  
**Improvement Suggestions:**  
Remove global state by passing the container explicitly:  
```python
def append_global(container, value):
    container.append(value)
    return container
```  
**Priority Level:** High  

---

### Code Smell Type: Unintended Input Mutation
**Problem Location:**  
`data[i] = data[i] * 2` in `mutate_input(data)`  
**Detailed Explanation:**  
The function mutates the caller's input list without documentation. This violates the "avoid modifying inputs" rule, as callers expect inputs to remain unaltered. Mutation causes hard-to-debug bugs (e.g., if the caller later relies on the original list).  
**Improvement Suggestions:**  
Either document mutation explicitly or avoid mutation:  
```python
# Option 1 (documented mutation)
def mutate_input(data):
    """Mutates input list in-place, doubling each element."""
    for i in range(len(data)):
        data[i] *= 2
    return data

# Option 2 (no mutation, return new list)
def double_list(values):
    return [v * 2 for v in values]
```  
**Priority Level:** Medium  

---

### Code Smell Type: Deeply Nested Conditionals
**Problem Location:**  
`nested_conditions(x)` function body  
**Detailed Explanation:**  
Three levels of nested `if` statements reduce readability and increase cognitive load. This violates the "single responsibility" principle by making logic hard to follow and maintain. For example, adding a new condition requires traversing multiple nested blocks.  
**Improvement Suggestions:**  
Flatten conditionals using early returns:  
```python
def nested_conditions(x):
    if x > 0:
        if x < 10:
            return "small even positive" if x % 2 == 0 else "small odd positive"
        return "medium positive" if x < 100 else "large positive"
    return "zero" if x == 0 else "negative"
```  
**Priority Level:** Medium  

---

### Code Smell Type: Overly Broad Exception Handling
**Problem Location:**  
`except Exception:` in `risky_division(a, b)`  
**Detailed Explanation:**  
Catching all exceptions (e.g., `KeyboardInterrupt`, `SystemExit`) masks critical errors. The function returns `None` for *any* exception, which could lead to unhandled `TypeError` later (e.g., if caller assumes a numeric return).  
**Improvement Suggestions:**  
Catch only expected exceptions:  
```python
def risky_division(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return None
```  
**Priority Level:** High  

---

### Code Smell Type: Inconsistent Return Types
**Problem Location:**  
`return 42` vs `return "forty-two"` in `inconsistent_return(flag)`  
**Detailed Explanation:**  
The function returns either an `int` or `str`, violating consistency. Callers must handle both types, increasing error risk (e.g., `TypeError` when concatenating strings with numbers).  
**Improvement Suggestions:**  
Standardize return type:  
```python
def consistent_return(flag):
    return 42 if flag else "42"
```  
**Priority Level:** High  

---

### Code Smell Type: Side Effect in List Comprehension
**Problem Location:**  
`side_effects = [print(i) for i in range(3)]`  
**Detailed Explanation:**  
List comprehensions are for building collections, not executing side effects (like `print`). This violates RAG rules and confuses readers (side effects are hidden in the comprehension).  
**Improvement Suggestions:**  
Use a regular `for` loop for side effects:  
```python
for i in range(3):
    print(i)
```  
**Priority Level:** Medium  

---

### Code Smell Type: Magic Number
**Problem Location:**  
`3.14159` in `calculate_area(radius)`  
**Detailed Explanation:**  
Hardcoded `3.14159` lacks context and precision. Using `math.pi` would be clearer and more accurate. Future changes (e.g., better pi approximation) require manual search-and-replace.  
**Improvement Suggestions:**  
Use `math.pi` or define a constant:  
```python
import math

def calculate_area(radius):
    return math.pi * radius * radius
```  
**Priority Level:** Low  

---

### Code Smell Type: Dangerous `eval` Usage
**Problem Location:**  
`return eval(code_str)` in `run_code(code_str)`  
**Detailed Explanation:**  
`eval` executes arbitrary code from `code_str`, enabling remote code execution (RCE) vulnerabilities. This is a critical security risk if input is untrusted.  
**Improvement Suggestions:**  
Replace with safe alternatives (e.g., `ast.literal_eval` for literals only):  
```python
import ast

def run_code(code_str):
    # Only safe for literals (e.g., "1 + 2"), NOT for arbitrary code.
    return ast.literal_eval(code_str)
```  
**Priority Level:** High