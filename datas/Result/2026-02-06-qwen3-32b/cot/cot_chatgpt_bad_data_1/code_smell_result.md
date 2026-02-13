### Code Smell Type: Global State Abuse
**Problem Location**:  
```python
cache = {}
results = []
```
and usage in `process_items` and `get_user_data`.
**Detailed Explanation**:  
Global variables create hidden dependencies and state that break modularity. The `results` list accumulates results across multiple function calls (e.g., `process_items` in `main` appends to the same global list), causing unexpected behavior. The cache is shared across all invocations, making tests impossible and leading to state pollution. This violates encapsulation and makes the code non-reentrant.
**Improvement Suggestions**:  
Replace global state with function parameters or a class. For example:  
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
**Priority Level**: High

---

### Code Smell Type: Unnecessary Use of `eval`
**Problem Location**:  
```python
return eval(f"{x} * {x}")
```
**Detailed Explanation**:  
`eval` introduces severe security risks (arbitrary code execution) and performance penalties. The function could simply return `x * x` without string parsing. This is a classic anti-pattern—using `eval` for basic arithmetic is both dangerous and inefficient.
**Improvement Suggestions**:  
Replace `eval` with direct multiplication:  
```python
def expensive_compute(x):
    if x == 0:
        return None
    if x < 0:
        return "invalid"
    return x * x  # Replaces eval
```
**Priority Level**: High

---

### Code Smell Type: Inconsistent Return Types
**Problem Location**:  
```python
if x == 0:
    return None
if x < 0:
    return "invalid"
return x * x
```
**Detailed Explanation**:  
The function returns `None`, string, or integer inconsistently. This forces callers to handle multiple types, increasing complexity and error risk. For example, `process_items` appends results to a list without type checks, which could break downstream logic (e.g., treating `"invalid"` as a number).
**Improvement Suggestions**:  
Standardize return types. Return `None` for all invalid inputs or use exceptions:  
```python
def expensive_compute(x):
    if x < 0:
        raise ValueError("Negative input")
    if x == 0:
        return None
    return x * x
```
**Priority Level**: High

---

### Code Smell Type: Side Effect in List Comprehension
**Problem Location**:  
```python
[results.append(cache[item])]
```
**Detailed Explanation**:  
List comprehensions are for *building* collections, not executing side effects. This confuses readers (who expect a new list) and violates the principle of least surprise. It also forces the reader to mentally parse the side effect, hurting readability.
**Improvement Suggestions**:  
Replace with a standard loop:  
```python
for item in items:
    if item not in cache:
        cache[item] = expensive_compute(item)
    time.sleep(0.01)
    results.append(cache[item])
```
**Priority Level**: Medium

---

### Code Smell Type: Unnecessary Sleep in Loop
**Problem Location**:  
```python
time.sleep(0.01)
```
**Detailed Explanation**:  
The sleep adds arbitrary latency without justification. It degrades performance (e.g., 10 items = 0.1s delay) and is a classic performance anti-pattern. The function does not require rate limiting or I/O, so this is a premature optimization.
**Improvement Suggestions**:  
Remove the sleep entirely. If rate limiting is needed, make it configurable and external to the function.  
**Priority Level**: Medium

---

### Code Smell Type: Ambiguous Function Name
**Problem Location**:  
```python
def get_user_data(user_input):
```
**Detailed Explanation**:  
The name suggests data retrieval from a user source, but the function simply returns cached values or the input string. This misleads readers about the function's purpose. The ambiguity is compounded by global cache usage.
**Improvement Suggestions**:  
Rename to reflect actual behavior (e.g., `get_cached_or_input`), or remove the function entirely if it’s redundant.  
**Priority Level**: Low

---

### Code Smell Type: Missing Documentation
**Problem Location**:  
No docstrings for functions.
**Detailed Explanation**:  
Lack of documentation impedes understanding of parameters, return values, and side effects. For example, `expensive_compute`’s inconsistent return types are unclear without context.
**Improvement Suggestions**:  
Add docstrings:  
```python
def expensive_compute(x: int) -> Union[int, None, str]:
    """Compute x squared. Returns None for 0, 'invalid' for negatives."""
```
**Priority Level**: Medium