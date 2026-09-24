### 1. **Global Variable Mutation**
- **Issue**: The code modifies global variables (`DATA_STORE`, `USER_COUNT`, `CONFIG`) directly.
- **Explanation**: Using globals makes it hard to track state changes and can cause unpredictable bugs.
- **Why it happens**: Not encapsulating shared data into a dedicated service or manager.
- **Impact**: Reduces testability and increases side effects.
- **Fix suggestion**: Encapsulate mutable data in a class or module-level manager.
```python
# Before
DATA_STORE.append(item)

# After
data_manager = DataManager()
data_manager.add_item(item)
```
- **Best Practice**: Prefer encapsulation over direct global access.

---

### 2. **Generic Exception Handling**
- **Issue**: Catches `Exception` without logging or re-raising.
- **Explanation**: Errors might be silently ignored, making debugging difficult.
- **Why it happens**: Lack of structured error handling.
- **Impact**: Can mask critical failures.
- **Fix suggestion**: Log the exception or raise a custom one.
```python
# Before
except Exception as e:

# After
except Exception as e:
    logger.error(f"Failed to add item: {e}")
    raise
```
- **Best Practice**: Handle exceptions explicitly and communicate failures clearly.

---

### 3. **Duplicated Logic Across Routes**
- **Issue**: Same logic appears in multiple places.
- **Explanation**: Repetition increases maintenance burden.
- **Why it happens**: Lack of abstraction for shared behavior.
- **Impact**: Bugs introduced when updating one copy but not others.
- **Fix suggestion**: Extract common code into a utility function.
```python
# Before
if condition: ...
if condition: ...

# After
def append_item_logic():
    # Common logic
```
- **Best Practice**: Follow DRY (Don’t Repeat Yourself).

---

### 4. **Hardcoded Configuration Values**
- **Issue**: Config values like `'mode'` and thresholds are hardcoded.
- **Explanation**: Makes deployment less flexible and harder to customize.
- **Why it happens**: No separation between code and environment-specific settings.
- **Impact**: Requires recompilation or redeployment for minor changes.
- **Fix suggestion**: Move config to environment variables or config files.
```python
# Before
CONFIG['mode'] = 'test'

# After
import os
MODE = os.getenv('MODE', 'default')
```
- **Best Practice**: Externalize configuration for different environments.

---

### 5. **Deeply Nested Conditionals**
- **Issue**: Complex nested `if` blocks reduce readability.
- **Explanation**: Harder to follow logic and prone to mistakes.
- **Why it happens**: Imperative style instead of functional decomposition.
- **Impact**: Increased cognitive load and error-prone.
- **Fix suggestion**: Use early returns or helper functions.
```python
# Before
if x > 0:
    if y < 100:
        if z == True:

# After
if not x > 0: return
if y >= 100: return
...
```
- **Best Practice**: Flatten control flow where possible.

---

### 6. **Unvalidated User Input**
- **Issue**: Inputs from `request.args` are used directly.
- **Explanation**: Could lead to invalid operations or security flaws.
- **Why it happens**: Skipping input sanitization and validation.
- **Impact**: Vulnerable to misuse or crashes.
- **Fix suggestion**: Validate all inputs before processing.
```python
# Before
value = request.args.get("key")

# After
value = request.args.get("key")
if not value:
    raise ValueError("Missing key")
```
- **Best Practice**: Always sanitize and validate user-provided data.

---

### 7. **Magic Numbers**
- **Issue**: Numeric literals like `100`, `10` appear without explanation.
- **Explanation**: Makes intent unclear and hard to update.
- **Why it happens**: No constant definitions for reused values.
- **Impact**: Maintenance overhead and confusion.
- **Fix suggestion**: Replace with named constants.
```python
# Before
if count > 100:

# After
MAX_ITEMS = 100
if count > MAX_ITEMS:
```
- **Best Practice**: Name magic numbers for clarity.

---