### 1. Unused Parameters  
**Issue**: Function `doSomething` declares parameters `g`, `h`, `i`, and `j` but never uses them.  
**Why It Happens**: The function signature was not updated after removing logic that required these parameters.  
**Impact**: Confuses callers (why are these parameters present?) and increases cognitive load during maintenance. Low risk for correctness but harms readability.  
**Fix**: Remove unused parameters:  
```python
# Before
def doSomething(a, b, c, d, e, f, g, h, i, j):
    ...

# After
def doSomething(a, b, c, d, e, f):
    ...
```  
**Best Practice**: *Keep parameters minimal and meaningful (DRY principle).*  

---

### 2. Deeply Nested Conditionals  
**Issue**: `doSomething` has 4 levels of nested conditionals.  
**Why It Happens**: Logic wasn’t refactored into guard clauses or helper functions.  
**Impact**: Hard to read, debug, and extend. Increases bug risk (e.g., missing edge cases). High severity for maintainability.  
**Fix**: Flatten with early returns:  
```python
# Before
if a > 10:
    if b < 5:
        if c == 3:
            ...

# After
if a <= 10:
    return -1  # Early exit
if b >= 5:
    return 42  # Early exit
# Rest of logic
```  
**Best Practice**: *Prefer guard clauses to reduce nesting (SOLID principle: Single Responsibility).*  

---

### 3. Inconsistent Return Types  
**Issue**: `doSomething` returns `float` in some branches and `int` in others.  
**Why It Happens**: Mixing arithmetic (division) and integer literals without type consistency.  
**Impact**: Runtime type errors (e.g., caller expects `int` but gets `float`). Severe for reliability.  
**Fix**: Normalize return types:  
```python
# Before
if d != 0:
    return (a * b * c) / d  # Float
else:
    return 999999            # Int

# After
return int((a * b * c) / d) if d != 0 else ERROR_VALUE  # Both integers
```  
**Best Practice**: *Functions should return consistent types (clarity > convenience).*  

---

### 4. Magic Number  
**Issue**: Hardcoded `999999` in `doSomething` (used as an error value).  
**Why It Happens**: Numeric values lack context or naming.  
**Impact**: Unclear meaning (why `999999`?), hard to change, and prone to typos. Medium severity.  
**Fix**: Define a named constant:  
```python
# Before
result = 999999

# After
ERROR_VALUE = 999999
result = ERROR_VALUE
```  
**Best Practice**: *Replace magic numbers with descriptive constants (e.g., `MAX_ERROR`).*  

---

### 5. Global Mutable State  
**Issue**: `processData` relies on global mutable list `dataList`.  
**Why It Happens**: Using global state instead of dependency injection.  
**Impact**: Breaks testability (can’t isolate `processData`), causes unexpected side effects. Critical for reliability.  
**Fix**: Pass data explicitly:  
```python
# Before
dataList = [1, 2, 3]  # Global

def processData():
    for k in range(len(dataList)):
        ...

# After
def processData(data: list):
    for value in data:  # Direct iteration
        ...
```  
**Best Practice**: *Avoid globals; use explicit dependencies (encapsulation principle).*  

---

### 6. Index-Based Iteration  
**Issue**: `processData` uses `for k in range(len(dataList))` instead of direct value iteration.  
**Why It Happens**: Not leveraging Python’s iterator-friendly syntax.  
**Impact**: Less readable, and risks off-by-one errors. Low severity but harms maintainability.  
**Fix**: Replace index iteration with direct value access:  
```python
# Before
for k in range(len(dataList)):
    value = dataList[k]

# After
for value in dataList:
    # Use `value` directly
```  
**Best Practice**: *Prefer `for value in collection` over index-based loops (Pythonic style).*