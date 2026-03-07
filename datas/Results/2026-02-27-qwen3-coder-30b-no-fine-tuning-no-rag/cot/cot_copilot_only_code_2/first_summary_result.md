### 📌 Pull Request Summary

- **Key Changes**  
  - Introduced `StringProcessor` and `NumberProcessor` classes to transform string and numeric data respectively.  
  - Added `DataPipeline` class to chain processing steps.  
  - Implemented conditional logic based on `GLOBAL_CONFIG`.

- **Impact Scope**  
  - Affects `DataPipeline`, `StringProcessor`, and `NumberProcessor`.  
  - Global configuration `GLOBAL_CONFIG` influences control flow in `main()`.

- **Purpose of Changes**  
  - Adds modular data transformation capabilities using a pipeline pattern.  
  - Enables conditional behavior based on global settings.

- **Risks and Considerations**  
  - Hardcoded values in conditionals may reduce flexibility.  
  - `GLOBAL_CONFIG` is mutable and could introduce unexpected behavior if modified elsewhere.  
  - Potential for logic errors in deeply nested conditionals.

- **Items to Confirm**  
  - Ensure `GLOBAL_CONFIG` remains static or is properly guarded.  
  - Validate that all edge cases in `StringProcessor` and `NumberProcessor` are covered.  
  - Confirm that nested `if` blocks are intentional and readable.

---

### ✅ Code Review Feedback

#### 1. **Readability & Consistency**
- ✅ Indentation and structure are consistent and clear.
- ⚠️ Comments are missing; consider adding brief docstrings or inline comments to explain transformations (e.g., what `StringProcessor` does).

#### 2. **Naming Conventions**
- ✅ Class names (`BaseProcessor`, `StringProcessor`, etc.) are descriptive and follow PascalCase.
- ⚠️ Variable names like `val`, `result`, and `ch` can be more descriptive (e.g., `input_char`, `processed_result`) for improved clarity.

#### 3. **Software Engineering Standards**
- ✅ Modular design with `DataPipeline` allows extensibility.
- ⚠️ Duplicate logic in `StringProcessor` and `NumberProcessor` (both check `isinstance` and fallback to parent). Could refactor into base class helper or shared interface.

#### 4. **Logic & Correctness**
- ⚠️ Deep nesting in `main()` makes it hard to read and debug. Consider flattening or extracting logic into functions.
- ⚠️ In `StringProcessor`, characters are converted to uppercase and non-alphabetic ones to their ASCII values — but this behavior might not be fully documented or tested.
- ❗ Risk of integer overflow or modulo behavior depending on input size in `NumberProcessor`.

#### 5. **Performance & Security**
- ⚠️ No explicit input sanitization or validation — could allow malicious inputs if used outside controlled environments.
- ⚠️ The use of `ord(ch)` without bounds checking may cause issues with Unicode characters or very long strings.

#### 6. **Documentation & Testing**
- ❌ Missing unit tests for `StringProcessor` and `NumberProcessor`.
- ⚠️ No inline or docstring comments explaining expected behavior of processors or configuration usage.

#### 7. **Scoring Overview**

| Category | Score |
|---------|-------|
| Readability & Consistency | ⭐⭐⭐⭐ |
| Naming Conventions | ⭐⭐⭐⭐ |
| Software Engineering | ⭐⭐⭐ |
| Logic & Correctness | ⭐⭐⭐ |
| Performance & Security | ⭐⭐ |
| Documentation & Testing | ⭐⭐ |

---

### 🔧 Suggestions for Improvement

1. **Refactor Nested Conditions**: Break down complex conditionals in `main()` into helper functions or early returns.
2. **Add Input Validation**: Validate input types and lengths before processing.
3. **Improve Test Coverage**: Add unit tests covering edge cases for both processors.
4. **Document Behavior**: Include docstrings and comments explaining how each processor transforms data.
5. **Avoid Mutable Global State**: Make `GLOBAL_CONFIG` immutable or pass as parameter to avoid side effects.

---

### 🧪 Example Test Cases to Add

```python
def test_string_processor():
    processor = StringProcessor()
    assert processor.process("abc123") == "ABC495051"  # 'a' -> 'A', 'b' -> 'B', 'c' -> 'C', '1' -> 49, '2' -> 50, '3' -> 51

def test_number_processor():
    processor = NumberProcessor()
    assert processor.process(7) == (7 * 1234) % 5678 + 9999
```

These additions will improve robustness, readability, and confidence in the system.