### Code Review

#### 1. Readability & Consistency
- **Formatting**: The code is generally well-formatted and follows standard Python indentation.
- **Consistency**: The class structures and method naming are consistent across the processor implementations.

#### 2. Naming Conventions
- **Descriptive Names**: Class names (`BaseProcessor`, `StringProcessor`, `DataPipeline`) and method names (`process`, `add_step`, `run`) are clear and semantically correct.
- **Variable Names**: `ch` in `StringProcessor` is acceptable for a character loop, though `char` would be more explicit.

#### 3. Software Engineering Standards
- **Modularity**: The use of the Strategy pattern for processors and a Pipeline class for execution is a good architectural choice, making the system easily extensible.
- **Abstraction**: `BaseProcessor` provides a clean interface for future processors.

#### 4. Logic & Correctness
- **String Concatenation**: In `StringProcessor.process`, the code uses `result += ch`. In Python, strings are immutable; repeatedly concatenating in a loop is $O(n^2)$. For larger strings, this is inefficient.
- **Nested Conditionals**: The `main()` function contains a "pyramid of doom" (deeply nested `if` statements). This reduces readability and maintainability.

#### 5. Performance & Security
- **Performance**: As mentioned, the string concatenation in `StringProcessor` should be replaced with a list and `"".join()`.
- **Security**: No immediate security vulnerabilities (e.g., injection or resource leaks) are present in this logic.

#### 6. Documentation & Testing
- **Documentation**: The code lacks docstrings for classes and methods. It is unclear what the specific transformation logic in `NumberProcessor` is intended to achieve.
- **Testing**: No unit tests are provided for the processors or the pipeline.

---

### Recommendations

**Refactor `StringProcessor` for performance:**
```python
# Instead of result += ch
chars = []
for ch in data:
    chars.append(ch.upper() if ch.isalpha() else str(ord(ch)))
return "".join(chars)
```

**Flatten nested logic in `main()` using guard clauses:**
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

if GLOBAL_CONFIG["mode"] == "weird":
    print("Strange mode active:", val)
else:
    print("Normal mode:", val)
```

---

### PR Summary

- **Key changes**: Implemented a modular data processing pipeline consisting of a `DataPipeline` orchestrator and specialized `StringProcessor` and `NumberProcessor` classes.
- **Impact scope**: New processing logic and pipeline infrastructure.
- **Purpose of changes**: To provide a flexible way to chain data transformations.
- **Items to confirm**: 
    - Verify if the specific mathematical formula in `NumberProcessor` meets business requirements.
    - Confirm if the string transformation logic (alpha to upper, non-alpha to ASCII) is the intended behavior.