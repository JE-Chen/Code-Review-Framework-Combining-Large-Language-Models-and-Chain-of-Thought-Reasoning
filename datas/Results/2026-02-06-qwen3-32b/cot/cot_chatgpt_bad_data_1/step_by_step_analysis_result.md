### 1. Global State Abuse  
**Issue**:  
Global variables `cache` and `results` create hidden dependencies and state pollution.  
**Context**:  
Global state breaks encapsulation, making functions non-reentrant and impossible to test in isolation. For example, `process_items` appends to the global `results` list, causing cumulative results across unrelated function calls.  

**Root Cause**:  
Hardcoded top-level state instead of using parameters or object-oriented composition.  

**Impact**:  
- **Critical**: Tests fail due to state leakage (e.g., cache persists between test cases).  
- **High**: Code becomes fragile; modifying global state accidentally breaks unrelated logic.  

**Fix**:  
Replace globals with class instance variables or function parameters:  
```python
class ItemProcessor:
    def __init__(self):
        self.cache = {}
    
    def process_items(self, items, verbose=False):
        results = []
        for item in items:
            if item not in self.cache:
                self.cache[item] = self.expensive_compute(item)
            time.sleep(0.01)
            results.append(self.cache[item])
        if verbose and len(results) > 10:
            print("Lots of results!")
        return results
```

**Best Practice**:  
Prefer dependency injection over global state (SOLID: Dependency Inversion Principle).  

---

### 2. Mutable Default Argument  
**Issue**:  
Default argument `items=[]` in a function may lead to unintended state sharing.  
**Context**:  
Mutable defaults are evaluated once at function definition. Subsequent calls reuse the *same list*, causing cumulative side effects (e.g., appending to the list across calls).  

**Root Cause**:  
Using a mutable object (`list`) as a default argument instead of `None`.  

**Impact**:  
- **High**: Silent bugs (e.g., a list grows unexpectedly across function invocations).  
- **Critical**: Hard to debug due to hidden state.  

**Fix**:  
Use `None` and initialize inside the function:  
```python
def process_items(items=None, verbose=False):
    if items is None:
        items = []  # Initialize fresh list per call
    # ... rest of logic
```

**Best Practice**:  
Always use `None` for mutable default arguments (Python Enhancement Proposals).  

---

### 3. Side Effect in List Comprehension  
**Issue**:  
List comprehension `[results.append(cache[item])]` executes a side effect instead of building a collection.  
**Context**:  
List comprehensions should return new collections, not mutate external state. This confuses readers (expecting a list of results, not a side effect).  

**Root Cause**:  
Misuse of list comprehensions for imperative code.  

**Impact**:  
- **Medium**: Reduced readability; violates "principle of least surprise."  
- **High**: Forces readers to mentally parse side effects, increasing cognitive load.  

**Fix**:  
Replace with a standard loop:  
```python
results = []
for item in items:
    if item not in cache:
        cache[item] = expensive_compute(item)
    time.sleep(0.01)
    results.append(cache[item])
```

**Best Practice**:  
Use list comprehensions *only* for building new collections (e.g., `[x * 2 for x in items]`).  

---

### 4. Unnecessary Sleep in Loop  
**Issue**:  
`time.sleep(0.01)` inside a loop adds artificial delay.  
**Context**:  
Sleeps degrade performance without justification (e.g., no rate limiting or I/O). For 100 items, this adds 1 second of delay.  

**Root Cause**:  
Arbitrary delay added without business need.  

**Impact**:  
- **Medium**: Poor performance; degrades user experience.  
- **High**: Unnecessary CPU idle time (wasted resources).  

**Fix**:  
Remove sleep unless explicitly required:  
```python
# Remove this line entirely
# time.sleep(0.01)
```

**Best Practice**:  
Avoid sleeps in business logic; externalize rate limits via configuration.  

---

### 5. Use of `eval`  
**Issue**:  
`eval(f"{x} * {x}")` introduces security and performance risks.  
**Context**:  
`eval()` executes arbitrary code, enabling remote code execution (RCE) vulnerabilities. The same result is achievable via direct math.  

**Root Cause**:  
Using `eval` for simple arithmetic instead of safe alternatives.  

**Impact**:  
- **Critical**: Security risk (e.g., attacker injects malicious code).  
- **High**: Slower execution (string parsing overhead).  

**Fix**:  
Replace with direct computation:  
```python
def expensive_compute(x):
    if x == 0:
        return None
    if x < 0:
        return "invalid"
    return x * x  # Safe and efficient
```

**Best Practice**:  
Never use `eval()` for user input or basic operations (Security Anti-Patterns).  

---

### 6. Cache Key Mismatch  
**Issue**:  
Cache keys are integers, but `get_user_data` accepts string inputs, causing cache misses.  
**Context**:  
`cache` uses integer keys (e.g., `cache[42]`), but `get_user_data` receives strings (e.g., `"42"`), so cache lookups always fail.  

**Root Cause**:  
Inconsistent type handling between cache storage and input.  

**Impact**:  
- **Critical**: Cache is effectively useless, defeating its purpose.  
- **High**: Repeated redundant computations.  

**Fix**:  
Normalize input types or use consistent keys:  
```python
def get_user_data(user_input: str) -> str:
    key = int(user_input)  # Convert to integer key
    if key in cache:
        return cache[key]
    # ... compute and store in cache
```

**Best Practice**:  
Ensure input/output types align with data structures (e.g., use consistent key types).  

---

### 7. Inconsistent Return Types  
**Issue**:  
`expensive_compute` returns `None`, string, or integer inconsistently.  
**Context**:  
Callers must handle multiple return types (e.g., `results.append(...)` silently accepts `"invalid"` as a string).  

**Root Cause**:  
Lack of type safety and error handling.  

**Impact**:  
- **Critical**: Runtime errors downstream (e.g., treating `"invalid"` as a number).  
- **High**: Increased complexity for callers.  

**Fix**:  
Standardize return types:  
```python
def expensive_compute(x: int) -> int | None:
    if x < 0:
        raise ValueError("Negative input")
    if x == 0:
        return None
    return x * x
```

**Best Practice**:  
Prefer exceptions over inconsistent return types (e.g., `raise ValueError` instead of returning `"invalid"`).