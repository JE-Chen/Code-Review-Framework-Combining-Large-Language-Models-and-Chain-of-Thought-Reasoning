### 1. **No Global Assign**
**Issue**:  
Assigning to a global variable `GLOBAL_SESSION` is discouraged.

**Explanation**:  
This linter rule warns against modifying shared state outside the scope of a function or class. It makes the code less predictable and harder to test.

**Root Cause**:  
Using global variables increases coupling and side effects.

**Impact**:  
Code behavior may vary depending on how globals are initialized or changed elsewhere.

**Fix**:  
Pass dependencies explicitly instead of relying on global state.

```python
# Instead of:
GLOBAL_SESSION = requests.Session()

# Do:
def create_session():
    return requests.Session()
```

**Best Practice**: Dependency injection promotes cleaner, more modular code.

---

### 2. **Unused Variables**
**Issue**:  
The variable `ANOTHER_GLOBAL` was declared but never used.

**Explanation**:  
Unused code clutters the logic and can mislead readers into thinking something important is happening.

**Root Cause**:  
Incomplete refactoring or lack of attention during development.

**Impact**:  
Maintains confusion and reduces readability.

**Fix**:  
Remove unused declarations.

```python
# Before
ANOTHER_GLOBAL = "https://jsonplaceholder.typicode.com/posts"

# After
# Remove unused line
```

**Best Practice**: Clean up dead code regularly.

---

### 3. **Magic Numbers**
**Issue**:  
Direct usage of `200` instead of a named constant.

**Explanation**:  
Hardcoded numbers make code harder to read and maintain.

**Root Cause**: Lack of abstraction for common values.

**Impact**:  
Changes require manual updates across multiple places.

**Fix**:  
Define constants with descriptive names.

```python
# Before
if response.status_code == 200:

# After
HTTP_OK = 200
if response.status_code == HTTP_OK:
```

**Best Practice**: Replace magic values with named constants.

---

### 4. **Catch Generic Exception**
**Issue**:  
Caught exception `Exception` without handling or re-raising.

**Explanation**:  
This hides unexpected errors and prevents debugging.

**Root Cause**: Overgeneralizing exception catching.

**Impact**: Silent failures and poor observability.

**Fix**: Catch specific exceptions or log and re-raise.

```python
# Before
try:
    ...
except Exception as e:

# After
try:
    ...
except requests.RequestException as e:
    logger.error(f"Request failed: {e}")
    raise
```

**Best Practice**: Handle known exceptions gracefully and propagate unknown ones.

---

### 5. **Empty Except Block**
**Issue**:  
An empty `except` block swallows all exceptions silently.

**Explanation**:  
Such blocks hide bugs and make diagnostics impossible.

**Root Cause**: Incomplete error management.

**Impact**: Masked runtime errors.

**Fix**: Log or raise exceptions.

```python
# Before
except:
    pass

# After
except Exception as e:
    logger.exception("Unexpected error occurred")
    raise
```

**Best Practice**: Never ignore exceptions.

---

### 6. **Console Logs**
**Issue**:  
Use of `print()` makes testing and deployment difficult.

**Explanation**:  
Print statements tie output to console and aren’t suitable for production systems.

**Impact**: Limits flexibility and traceability.

**Fix**: Use structured logging instead.

```python
# Before
print("Response received")

# After
import logging
logger.info("Response received")
```

**Best Practice**: Prefer logs over prints for better control.

---

### 7. **Long Function**
**Issue**:  
One function handles too many unrelated tasks.

**Explanation**:  
Violates the Single Responsibility Principle.

**Impact**: Difficult to debug, extend, or reuse.

**Fix**: Decompose into smaller, focused helpers.

```python
# Before
def complex_function():
    # Fetch, process, log, post...

# After
def fetch_data():
    ...

def send_post():
    ...

def log_result():
    ...
```

**Best Practice**: Each function should do one thing well.

---

### 8. **Implicit Boolean Check**
**Issue**:  
Using `== 200` instead of checking `response.ok`.

**Explanation**:  
Less readable and not idiomatic for HTTP responses.

**Impact**: Misleading comparisons.

**Fix**: Prefer standard properties like `.ok`.

```python
# Before
if response.status_code == 200:

# After
if response.ok:
```

**Best Practice**: Leverage built-in response attributes when available.

---