### 1. **Global Variable (`total_result`)**  
**Issue**:  
Global variable `total_result` creates hidden coupling and breaks testability.  
**Meaning**:  
Using global state makes code unpredictable and hard to isolate for testing. Changes to `total_result` affect unrelated parts of the code.  

**Root Cause**:  
Accidental use of `global` keyword to mutate a shared variable instead of returning results.  

**Impact**:  
- *High risk*: Tests cannot run independently (e.g., test A alters `total_result` used by test B).  
- *Maintainability*: Hard to track where `total_result` is modified.  

**Fix**:  
Replace global mutation with explicit return values:  
```python
# Before
total_result = 0
def doStuff(...):
    global total_result
    total_result += result

# After
def doStuff(...):
    return result  # Return value instead of mutating global

def processEverything(data):
    return sum(doStuff(item) for item in data)  # Accumulate in caller
```

**Best Practice**:  
*Prefer pure functions* (no side effects) for testability and composability.  

---

### 2. **Mutable Default Argument (`bucket=[]`)**  
**Issue**:  
Mutable default `bucket=[]` shared across all calls causes unexpected behavior.  
**Meaning**:  
Default arguments are evaluated *once* at function definition, not per call.  

**Root Cause**:  
Using a mutable object (like `list`) as a default value.  

**Impact**:  
- *Critical*: `collectValues(1)` appends to a shared list, breaking subsequent calls:  
  ```python
  collectValues(1)  # Returns [1]
  collectValues(2)  # Returns [1, 2] (not [2] as expected)
  ```  
- *Testability*: Impossible to reset state between tests.  

**Fix**:  
Use `None` as the default and initialize inside:  
```python
# Before
def collectValues(x, bucket=[]):
    bucket.append(x)
    return bucket

# After
def collectValues(x, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(x)
    return bucket
```

**Best Practice**:  
*Never use mutable objects as default arguments*.  

---

### 3. **Poor Naming (`a`, `b`, `c`)**  
**Issue**:  
Non-descriptive parameter names like `a`, `b`, `c` obscure intent.  
**Meaning**:  
Readers must reverse-engineer what parameters represent.  

**Root Cause**:  
Lazy naming without considering future maintainers.  

**Impact**:  
- *Readability*: Code becomes "magic" (e.g., `doStuff(10, "square", 5, ...)`).  
- *Maintainability*: Hard to refactor or extend without confusion.  

**Fix**:  
Use meaningful names:  
```python
# Before
def doStuff(a, b, c, ...):

# After
def doStuff(input_value, shape_type, radius, ...):
```

**Best Practice**:  
*Names should describe *purpose*, not *type* (e.g., `user_id` not `id`).*  

---

### 4. **Too Many Parameters (10)**  
**Issue**:  
Function with 10 parameters is hard to maintain and test.  
**Meaning**:  
Parameters overwhelm the interface, increasing cognitive load.  

**Root Cause**:  
No grouping of related parameters (e.g., `a` and `b` both describe input data).  

**Impact**:  
- *Testability*: Requires 2^10 test cases for edge coverage.  
- *Maintainability*: Adding new features forces signature changes.  

**Fix**:  
Group parameters into a configuration object:  
```python
# Before
def doStuff(a, b, c, d, e, f, g, h, i, j):

# After
class InputConfig:
    def __init__(self, value, shape, radius, ...): ...

def doStuff(config):
    # Use config.value, config.shape, etc.
```

**Best Practice**:  
*Prefer objects over primitive obsession* (reduces parameter count).  

---

### 5. **Deep Nesting (7 levels)**  
**Issue**:  
7 levels of nested conditionals impair readability and testability.  
**Meaning**:  
Logic is buried in complexity, making bugs hard to find.  

**Root Cause**:  
Failure to extract conditionals into focused helper functions.  

**Impact**:  
- *Readability*: Requires mental stack to track logic flow.  
- *Testability*: Each nested level requires additional test cases.  

**Fix**:  
Refactor into small functions:  
```python
# Before (deeply nested)
if d:
    if e:
        if f:
            ...  # 7 levels

# After (flat structure)
def calculate_z(x, y, d, e, f, g, h):
    if not d: return y
    if not e: return x
    if not f: return x * y
    ...
```

**Best Practice**:  
*Reduce nesting via early returns* (e.g., guard clauses).  

---

### 6. **Redundant Calculation (`temp1 = z + 1`)**  
**Issue**:  
Redundant math (`temp1 = z + 1`, `temp2 = temp1 - 1`) is equivalent to `z`.  
**Meaning**:  
Code adds noise without value.  

**Root Cause**:  
Copy-paste logic without verifying mathematical equivalence.  

**Impact**:  
- *Performance*: Unnecessary arithmetic operations.  
- *Readability*: Confuses intent (e.g., "Why add then subtract?").  

**Fix**:  
Replace with direct assignment:  
```python
# Before
temp1 = z + 1
temp2 = temp1 - 1
result = temp2

# After
result = z
```

**Best Practice**:  
*Remove redundant operations* (they increase bug surface area).  

---

### 7. **Unnecessary Sleep (`time.sleep(0.01)`)**  
**Issue**:  
Hardcoded `time.sleep(0.01)` harms performance without justification.  
**Meaning**:  
Adds artificial delay in hot paths, degrading throughput.  

**Root Cause**:  
Misunderstanding of performance requirements (e.g., "sleep fixes race conditions").  

**Impact**:  
- *Performance*: 100x slower in loops (e.g., 100ms per iteration).  
- *Non-determinism*: Sleep duration varies by system load.  

**Fix**:  
Remove the sleep entirely:  
```python
# Before
time.sleep(0.01)

# After
# (No sleep)
```

**Best Practice**:  
*Avoid sleeps in business logic* (use explicit timeouts if needed).  

---

### 8. **Error-Prone Type Checking (`type(item) == int`)**  
**Issue**:  
Using `type(item) == int` instead of `isinstance(item, int)`.  
**Meaning**:  
`type()` fails for subclassed types (e.g., `class MyInt(int): ...`), while `isinstance` works correctly.  

**Root Cause**:  
Ignoring Python's dynamic typing best practices.  

**Impact**:  
- *Correctness*: Fails for custom types (e.g., `MyInt` instance treated as non-`int`).  
- *Robustness*: Silent data corruption (e.g., rejecting valid inputs).  

**Fix**:  
Replace with `isinstance`:  
```python
# Before
if type(item) == int:

# After
if isinstance(item, int):
```

**Best Practice**:  
*Prefer `isinstance` over `type()` for type checks*.  

---

### 9. **Shadow Built-in (`sum`)**  
**Issue**:  
Variable `sum` shadows the built-in function.  
**Meaning**:  
Overwriting `sum` breaks its usage (e.g., `sum([1,2,3])` fails).  

**Root Cause**:  
Using common names without checking against built-ins.  

**Impact**:  
- *Breakage*: Code crashes when calling built-ins later.  
- *Confusion*: Readers assume `sum` is a variable, not a function.  

**Fix**:  
Rename to avoid shadowing:  
```python
# Before
sum = 0  # Shadows built-in

# After
total_sum = 0
```

**Best Practice**:  
*Avoid shadowing built-ins* (e.g., `sum`, `list`, `str`).  

---

### 10. **Redundant Conversion (`float(str(sum))`)**  
**Issue**:  
Unnecessary `float(str(sum))` loses precision and is inefficient.  
**Meaning**:  
Converting to string then back to float is redundant (use `float(sum)` directly).  

**Root Cause**:  
Misunderstanding of type conversion needs.  

**Impact**:  
- *Precision loss*: `float("1.234567890123456789")` may round to `1.23456789`.  
- *Performance*: Extra string allocation and parsing.  

**Fix**:  
Return the value directly:  
```python
# Before
result = float(str(sum))

# After
result = sum  # Or float(sum) if needed
```

**Best Practice**:  
*Avoid redundant type conversions* (they add cognitive and runtime cost).