### 1. **Broad Exception Handling (`no-broad-exception`)**
#### ✅ Problem:
Catching `Exception` hides unexpected errors, making debugging difficult.

#### 🧠 Root Cause:
Using a broad exception handler catches all errors, including programming mistakes or unhandled edge cases.

#### ⚠️ Impact:
- Masks real bugs.
- Makes logs less useful.
- Reduces reliability.

#### 💡 Fix:
Replace with specific exceptions or log and re-raise.

```python
# Before
try:
    risky_division(a, b)
except Exception as e:
    print("Error occurred")

# After
try:
    risky_division(a, b)
except ZeroDivisionError:
    print("Cannot divide by zero")
except ValueError:
    print("Invalid input")
```

#### ✅ Best Practice:
Always catch known exceptions and let unknown ones bubble up unless you have a good reason to suppress them.

---

### 2. **Inconsistent Return Types (`inconsistent-return-types`)**
#### ✅ Problem:
Functions return different types depending on execution path.

#### 🧠 Root Cause:
No clear contract about what a function should return — leads to confusion and runtime errors.

#### ⚠️ Impact:
Harder to write robust clients. Risk of type mismatch at runtime.

#### 💡 Fix:
Standardize return types. Prefer raising exceptions over returning sentinel values.

```python
# Before
def convert_to_int(s):
    try:
        return int(s)
    except:
        return -999  # magic number!

# After
def convert_to_int(s):
    try:
        return int(s)
    except ValueError:
        raise InvalidInputError("Cannot convert to integer")
```

#### ✅ Best Practice:
Define and stick to consistent return contracts for functions.

---

### 3. **Magic Numbers/Constants**
#### ✅ Problem:
Hardcoded values reduce clarity and maintainability.

#### 🧠 Root Cause:
No semantic meaning assigned to raw numbers or strings.

#### ⚠️ Impact:
Confusing for new developers. Difficult to update or refactor later.

#### 💡 Fix:
Use named constants or enums.

```python
# Before
return -1

# After
INVALID_VALUE = -1
return INVALID_VALUE
```

#### ✅ Best Practice:
Avoid magic numbers. Replace them with descriptive names or custom exceptions.

---

### 4. **Resource Leak (`no-resource-leak`)**
#### ✅ Problem:
File handles are not closed properly.

#### 🧠 Root Cause:
Manual resource management without context managers.

#### ⚠️ Impact:
Potential memory leaks or corrupted files if exceptions occur.

#### 💡 Fix:
Use `with` statements for automatic cleanup.

```python
# Before
f = open("data.txt", "r")
content = f.read()
f.close()

# After
with open("data.txt", "r") as f:
    content = f.read()
```

#### ✅ Best Practice:
Always use context managers when working with resources like files or network connections.

---

### 5. **Duplicate Code**
#### ✅ Problem:
Repeated file I/O logic across modules.

#### 🧠 Root Cause:
Lack of abstraction or reuse of common patterns.

#### ⚠️ Impact:
More code to maintain and debug.

#### 💡 Fix:
Create reusable utilities or wrappers.

```python
# Example: Utility function
def safe_read_file(filename):
    try:
        with open(filename, "r") as f:
            return f.read()
    except FileNotFoundError:
        return None
```

#### ✅ Best Practice:
Apply DRY (Don’t Repeat Yourself) principle. Extract shared logic into helpers or classes.

---

### 6. **Poor Error Propagation**
#### ✅ Problem:
Errors are caught and logged, but not propagated further.

#### 🧠 Root Cause:
Silent failure instead of graceful degradation or user feedback.

#### ⚠️ Impact:
System behavior becomes unpredictable. Users cannot react to problems.

#### 💡 Fix:
Re-raise exceptions or return explicit error indicators.

```python
# Before
try:
    process_data(...)
except Exception:
    logger.error("Processing failed")

# After
try:
    result = process_data(...)
except ProcessingError:
    logger.error("Processing failed")
    raise  # Or return error object
```

#### ✅ Best Practice:
Handle errors explicitly and propagate meaningful exceptions upward.

---

### 7. **Unnecessary Nesting**
#### ✅ Problem:
Deeply nested try-except blocks reduce readability.

#### 🧠 Root Cause:
Complex logic packed into one place.

#### ⚠️ Impact:
Harder to follow control flow and test individual parts.

#### 💡 Fix:
Break large blocks into smaller, focused functions.

```python
# Instead of deep nesting
try:
    ...
    try:
        ...
    except Exception:
        ...
except Exception:
    ...

# Break into helper functions
handle_inner_logic()
```

#### ✅ Best Practice:
Keep functions flat and modular. Each block should do one thing well.

---

### 8. **Global State Usage**
#### ✅ Problem:
Direct dependency on fixed file name.

#### 🧠 Root Cause:
Tight coupling to environment or configuration.

#### ⚠️ Impact:
Less portable and harder to unit test.

#### 💡 Fix:
Accept path as parameter or use config.

```python
# Before
main():
    read_file("data.txt")

# After
main(filepath="data.txt"):
    read_file(filepath)
```

#### ✅ Best Practice:
Make dependencies explicit and configurable rather than hardcoded.

---