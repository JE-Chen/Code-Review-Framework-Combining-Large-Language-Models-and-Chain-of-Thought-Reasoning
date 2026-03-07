---

### **Code Smell Type:** Mutable Default Argument  
**Problem Location:**  
```python
def add_item(item, container=[]):
```
**Detailed Explanation:**  
Using a mutable default argument (`container=[]`) leads to shared state across function calls because defaults are evaluated once at function definition time. This can result in unexpected behavior where modifications persist across multiple invocations. For example, calling `add_item("a")` and then `add_item("b")` will result in both items being added to the same list.

**Improvement Suggestions:**  
Replace the default with `None` and initialize the list inside the function body:
```python
def add_item(item, container=None):
    if container is None:
        container = []
    container.append(item)
    return container
```

**Priority Level:** High  

---

### **Code Smell Type:** Global State Mutation  
**Problem Location:**  
```python
shared_list = []
def append_global(value):
    shared_list.append(value)
    return shared_list
```
**Detailed Explanation:**  
Mutating a global variable introduces hidden dependencies and makes testing difficult. It also increases coupling between components, reducing modularity and making future changes more error-prone.

**Improvement Suggestions:**  
Pass `shared_list` as an argument or encapsulate it within a class or module-level structure that exposes controlled access rather than relying on global mutation.

**Priority Level:** High  

---

### **Code Smell Type:** Input Mutation Without Clear Documentation  
**Problem Location:**  
```python
def mutate_input(data):
    for i in range(len(data)):
        data[i] = data[i] * 2
    return data
```
**Detailed Explanation:**  
The function modifies its input directly without clear indication in the signature or documentation. This can lead to unintended side effects for callers expecting immutability.

**Improvement Suggestions:**  
Either document that input is mutated or return a new copy of the data:
```python
def mutate_input(data):
    return [x * 2 for x in data]
```

**Priority Level:** Medium  

---

### **Code Smell Type:** Deeply Nested Conditions  
**Problem Location:**  
```python
def nested_conditions(x):
    if x > 0:
        if x < 10:
            ...
```
**Detailed Explanation:**  
Deep nesting reduces readability and increases cognitive load. It is harder to debug, test, and extend. Flattening conditionals improves maintainability.

**Improvement Suggestions:**  
Refactor using guard clauses or early returns:
```python
def nested_conditions(x):
    if x <= 0:
        if x == 0:
            return "zero"
        else:
            return "negative"
    elif x < 10:
        return "small even positive" if x % 2 == 0 else "small odd positive"
    elif x < 100:
        return "medium positive"
    else:
        return "large positive"
```

**Priority Level:** Medium  

---

### **Code Smell Type:** Overly Broad Exception Handling  
**Problem Location:**  
```python
def risky_division(a, b):
    try:
        return a / b
    except Exception:
        return None
```
**Detailed Explanation:**  
Catching generic exceptions like `Exception` hides important errors and prevents proper error propagation. This makes debugging harder and can mask actual failures.

**Improvement Suggestions:**  
Catch specific exceptions such as `ZeroDivisionError`:
```python
def risky_division(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return None
```

**Priority Level:** Medium  

---

### **Code Smell Type:** Inconsistent Return Types  
**Problem Location:**  
```python
def inconsistent_return(flag):
    if flag:
        return 42
    else:
        return "forty-two"
```
**Detailed Explanation:**  
Returning different types from the same function increases complexity for callers who must handle various return values. This breaks predictability and can lead to runtime errors.

**Improvement Suggestions:**  
Return consistent types (e.g., always strings or integers), or introduce a wrapper type if needed:
```python
def inconsistent_return(flag):
    return str(42) if flag else "forty-two"
```

**Priority Level:** High  

---

### **Code Smell Type:** Redundant Work Inside Loop  
**Problem Location:**  
```python
def compute_in_loop(values):
    results = []
    for v in values:
        if v < len(values):  # Repeated len() call
            results.append(v * 2)
    return results
```
**Detailed Explanation:**  
Repeatedly computing `len(values)` inside the loop is inefficient since the length doesn’t change. Precomputing or caching this value improves performance and clarity.

**Improvement Suggestions:**  
Cache the length outside the loop:
```python
def compute_in_loop(values):
    n = len(values)
    results = []
    for v in values:
        if v < n:
            results.append(v * 2)
    return results
```

**Priority Level:** Medium  

---

### **Code Smell Type:** Side Effects in List Comprehension  
**Problem Location:**  
```python
side_effects = [print(i) for i in range(3)]
```
**Detailed Explanation:**  
List comprehensions should be used solely for building collections. Using them for side effects like printing violates intent and can make code harder to reason about.

**Improvement Suggestions:**  
Use a regular loop instead:
```python
for i in range(3):
    print(i)
```

**Priority Level:** Medium  

---

### **Code Smell Type:** Magic Number Usage  
**Problem Location:**  
```python
def calculate_area(radius):
    return 3.14159 * radius * radius
```
**Detailed Explanation:**  
Hardcoded constants reduce readability and make updates harder. If the value needs to be changed later, you might miss places where it's used.

**Improvement Suggestions:**  
Define π as a named constant:
```python
PI = 3.14159
def calculate_area(radius):
    return PI * radius * radius
```

**Priority Level:** Low  

---

### **Code Smell Type:** Use of `eval()`  
**Problem Location:**  
```python
def run_code(code_str):
    return eval(code_str)
```
**Detailed Explanation:**  
Using `eval()` introduces severe security vulnerabilities by allowing arbitrary code execution. Even if trusted input, it undermines safety guarantees and design principles.

**Improvement Suggestions:**  
Avoid `eval()` entirely unless absolutely necessary. If dynamic evaluation is required, consider safer alternatives like AST parsing or restricted interpreters.

**Priority Level:** High  

---