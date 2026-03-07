### Code Smell Type: Magic Numbers
**Problem Location**:  
`NumberProcessor.process` method:
```python
def process(self, data):
    if isinstance(data, int):
        return (data * 1234) % 5678 + 9999
    return super().process(data)
```

**Detailed Explanation**:  
The numbers `1234`, `5678`, and `9999` are arbitrary and lack context. This violates maintainability best practices by making the code harder to understand and modify. If these values need adjustment (e.g., for new requirements), they must be searched for manually across the codebase. The lack of descriptive names also obscures the business intent behind the transformation.

**Improvement Suggestions**:  
Replace magic numbers with named constants:
```python
# In a config module or class:
TRANSFORM_MULTIPLIER = 1234
TRANSFORM_MODULUS = 5678
TRANSFORM_OFFSET = 9999

# Then in NumberProcessor:
return (data * TRANSFORM_MULTIPLIER) % TRANSFORM_MODULUS + TRANSFORM_OFFSET
```
Document the constants' purpose in comments.

**Priority Level**: Medium  
*(Critical for maintainability but not a runtime bug)*

---

### Code Smell Type: Deeply Nested Conditionals
**Problem Location**:  
`main` function:
```python
if GLOBAL_CONFIG["flag"]:
    if val > 5:
        if val < GLOBAL_CONFIG["threshold"]:
            if GLOBAL_CONFIG["mode"] == "weird":
                print("Strange mode active:", val)
            else:
                print("Normal mode:", val)
        else:
            print("Value too large")
    else:
        print("Value too small")
else:
    print("Flag disabled")
```

**Detailed Explanation**:  
Four levels of nesting reduce readability and increase cognitive load. This structure makes it difficult to:
- Understand the flow without tracing multiple conditionals.
- Add new branches without further nesting.
- Prevent logical errors (e.g., missing edge cases).
The code violates the principle of "guard clauses" for early exits.

**Improvement Suggestions**:  
Flatten conditionals using early returns and guard clauses:
```python
if not GLOBAL_CONFIG["flag"]:
    print("Flag disabled")
    return

if val <= 5:
    print("Value too small")
    return

if val >= GLOBAL_CONFIG["threshold"]:
    print("Value too large")
    return

print("Strange mode active:", val) if GLOBAL_CONFIG["mode"] == "weird" else print("Normal mode:", val)
```
Extract helper methods for complex logic.

**Priority Level**: Medium  
*(Hampers readability and future changes)*

---

### Code Smell Type: Inefficient String Concatenation
**Problem Location**:  
`StringProcessor.process` method:
```python
result = ""
for ch in data:
    if ch.isalpha():
        result += ch.upper()
    else:
        result += str(ord(ch))
```

**Detailed Explanation**:  
Repeated string concatenation in a loop causes O(n²) performance due to Python's string immutability. This becomes problematic for large inputs (e.g., strings >1000 characters). The code smells like a classic "string building anti-pattern" that should use list accumulation followed by `join()`.

**Improvement Suggestions**:  
Replace with list comprehension and `join()`:
```python
chars = []
for ch in data:
    if ch.isalpha():
        chars.append(ch.upper())
    else:
        chars.append(str(ord(ch)))
return ''.join(chars)
```
*Note: Also fix the non-alphabetic handling (e.g., `ord(ch)` returns integer, but `str(ord(ch))` is correct here).*

**Priority Level**: Medium  
*(Performance impact only for large inputs, but standard best practice)*

---

### Code Smell Type: Global Configuration Variable
**Problem Location**:  
`GLOBAL_CONFIG` at module level:
```python
GLOBAL_CONFIG = {
    "mode": "weird",
    "threshold": 123456,
    "flag": True
}
```

**Detailed Explanation**:  
Global state creates hidden dependencies and breaks testability. Changes to `GLOBAL_CONFIG` can silently affect unrelated parts of the code. It also violates the Single Responsibility Principle by conflating configuration with business logic.

**Improvement Suggestions**:  
Inject configuration as a dependency:
```python
class DataPipeline:
    def __init__(self, config):
        self.config = config  # Injected dependency

# Usage:
config = {"mode": "weird", "threshold": 123456, "flag": True}
pipeline = DataPipeline(config)
```
Prefer immutable configuration objects over mutable globals.

**Priority Level**: Medium  
*(Critical for testability and scalability)*

---

### Code Smell Type: Weak Base Class
**Problem Location**:  
`BaseProcessor` class:
```python
class BaseProcessor:
    def process(self, data):
        return data
```

**Detailed Explanation**:  
The base class provides no useful abstraction—it merely returns the input. This forces subclasses to handle all logic while the base class adds no value. It violates the Liskov Substitution Principle (subclasses should extend behavior, not override it with minimal logic).

**Improvement Suggestions**:  
- Remove `BaseProcessor` entirely if it serves no purpose.  
- Or define a meaningful abstract method:
  ```python
  class BaseProcessor:
      def process(self, data):
          raise NotImplementedError("Subclasses must implement process()")
  ```
  *(Only if subclasses are guaranteed to override it.)*

**Priority Level**: Low  
*(Not critical but cleaner code)*

---

### Code Smell Type: Lack of Documentation
**Problem Location**:  
All classes and methods lack docstrings.

**Detailed Explanation**:  
No documentation explains:
- Purpose of `StringProcessor` (e.g., "Converts strings to uppercase + ASCII codes").
- Expected inputs/outputs for `DataPipeline`.
- Meaning of `GLOBAL_CONFIG` keys.
This increases onboarding time and risks misuse.

**Improvement Suggestions**:  
Add docstrings:
```python
class StringProcessor(BaseProcessor):
    """Processes strings by converting alphabetic chars to uppercase and non-alphabetic to ASCII codes."""
    def process(self, data):
        # ...
```
Document `DataPipeline`'s `run` method: "Executes all processors in order on input data."

**Priority Level**: Low  
*(Quality-of-life improvement, not a bug)*