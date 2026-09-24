Here is the code review based on the provided global rules.

### 1. Readability & Consistency
*   **Formatting:** The code is generally well-formatted and follows standard Python indentation.
*   **Consistency:** The class structures are consistent, and the pipeline pattern is implemented clearly.

### 2. Naming Conventions
*   **Descriptive Names:** Class names (`BaseProcessor`, `DataPipeline`) and method names (`process`, `add_step`, `run`) are semantic and follow standard naming conventions.
*   **Variable Names:** `ch` in `StringProcessor` is acceptable for a character loop, though `char` would be slightly more explicit.

### 3. Software Engineering Standards
*   **Modularity:** The use of the Strategy pattern (via `BaseProcessor`) makes the pipeline highly modular and extensible.
*   **Abstraction:** The `BaseProcessor` provides a clean interface for new processors to be added without modifying the `DataPipeline` class.

### 4. Logic & Correctness
*   **String Concatenation Performance:** In `StringProcessor`, `result += ch.upper()` is used inside a loop. In Python, strings are immutable; repeated concatenation creates new string objects. For very large input strings, this will lead to $O(n^2)$ complexity.
    *   *Recommendation:* Use a list to collect characters and `''.join(list)` at the end.
*   **Deep Nesting:** The `main()` function contains a "pyramid of doom" (four levels of nested `if` statements). This reduces readability and maintainability.
    *   *Recommendation:* Use guard clauses (early returns/continues) to flatten the logic.

### 5. Performance & Security
*   **Complexity:** As noted in Logic & Correctness, the string building is a performance bottleneck for large inputs.
*   **Security:** No external inputs are processed; however, if `input_data` were to come from a user, the current logic is safe as it only performs basic transformations.

### 6. Documentation & Testing
*   **Documentation:** The code lacks docstrings. While the logic is simple, the purpose of the "weird" transformations in `StringProcessor` and `NumberProcessor` is not documented.
*   **Testing:** No unit tests are provided for the individual processors or the pipeline orchestration.

---

### Summary of Findings

| Category | Status | Note |
| :--- | :--- | :--- |
| **Readability** | Pass | Clean and consistent. |
| **Naming** | Pass | Semantic and clear. |
| **Engineering** | Pass | Good use of polymorphism. |
| **Logic** | Warning | String concatenation efficiency and deep nesting. |
| **Performance** | Warning | $O(n^2)$ string building. |
| **Documentation** | Fail | Missing docstrings and unit tests. |

### Suggested Refactoring (Snippet)

**Flattening the nested logic in `main()`:**
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