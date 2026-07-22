### 1. **Unused Variable (`no-unused-vars`)**
#### ✅ **Issue**
The variable `val` is assigned but only used inside conditional checks. It’s not actually consumed afterward.

#### 🧠 **Root Cause**
This often results from temporary debugging or incomplete refactoring where variables were left behind.

#### ⚠️ **Impact**
- Reduces readability.
- Confuses future developers who see unused code.

#### 💡 **Fix**
Either remove the unused assignment or refactor logic to make full use of the variable.
```python
# Before
if val > 5:
    if val < threshold:
        # ... some logic
        pass
else:
    val = 10  # Unused after this point

# After
if val > 5 and val < threshold:
    # ... handle condition
    pass
```

#### 🌟 **Best Practice**
Avoid assigning values you don’t fully consume — keep assignments meaningful and necessary.

---

### 2. **Complex Nested Conditions (`complexity`)**
#### ✅ **Issue**
Deeply nested `if` statements make it hard to follow execution paths.

#### 🧠 **Root Cause**
Lack of early returns or helper functions leads to complex branching logic.

#### ⚠️ **Impact**
Harder to read, test, and debug; increases chance of logic errors.

#### 💡 **Fix**
Break down conditions using guard clauses or extract logic into helper functions.
```python
# Before
if flag:
    if val > 5:
        if val < threshold:
            if mode == "weird":
                ...

# After
def evaluate_conditions(flag, val, threshold, mode):
    if not flag:
        return False
    if val <= 5 or val >= threshold:
        return False
    return mode == "weird"
```

#### 🌟 **Best Practice**
Prefer flat structures over deeply nested ones. Use early exits and clear function boundaries.

---

### 3. **Magic Number (`magic-numbers`)**
#### ✅ **Issue**
A numeric literal `123456` appears without explanation or reuse.

#### 🧠 **Root Cause**
Constants are hardcoded instead of being given semantic meaning.

#### ⚠️ **Impact**
Makes code brittle and unclear when values change or need explanation.

#### 💡 **Fix**
Define named constants for such values.
```python
DEFAULT_THRESHOLD = 123456
...
if data > DEFAULT_THRESHOLD:
    ...
```

#### 🌟 **Best Practice**
Replace magic numbers with descriptive constants to improve readability and maintainability.

---

### 4. **Hardcoded String Value (`hardcoded-values`)**
#### ✅ **Issue**
String `'weird'` is used directly without abstraction.

#### 🧠 **Root Cause**
Configuration values are treated as literals rather than managed entities.

#### ⚠️ **Impact**
Fragile and hard to update if multiple places reference it.

#### 💡 **Fix**
Use a constant or enum.
```python
MODE_WEIRD = "weird"
...
if mode == MODE_WEIRD:
    ...
```

#### 🌟 **Best Practice**
Avoid hardcoding configuration values; manage them through constants or configuration files.

---

### 5. **Inconsistent Naming (`inconsistent-naming`)**
#### ✅ **Issue**
Class name `DataPipeline` uses PascalCase while Python typically prefers snake_case.

#### 🧠 **Root Cause**
Misalignment with language conventions or inconsistent team standards.

#### ⚠️ **Impact**
Lowers code consistency and readability for Python developers.

#### 💡 **Fix**
Rename class to match Python naming conventions.
```python
class data_pipeline:
    ...
```

#### 🌟 **Best Practice**
Follow PEP 8 style guide for Python code to ensure consistency and professionalism.

---