### Pull Request Summary

*   **Key changes**: Implemented a modular data processing pipeline using a base processor class and specific implementations for strings and numbers.
*   **Purpose of changes**: To create a flexible system for sequential data transformation.
*   **Items to confirm**: Review the logic in `StringProcessor` and the conditional nesting in `main()`.

---

### Code Review

#### 1. Logic & Correctness
*   **`StringProcessor.process`**: The logic converts alphabetic characters to uppercase and non-alphabetic characters to their Unicode integer representation. While functional, the result is a string of mixed characters and numbers, which may be difficult to reverse or parse.

#### 2. Software Engineering Standards
*   **Modular Design**: The use of the Strategy pattern (`BaseProcessor` and its subclasses) is well-implemented, making the pipeline easily extensible.

#### 3. Performance & Security
*   **String Concatenation**: In `StringProcessor.process`, `result += ...` is used inside a loop. In Python, strings are immutable, so this creates a new string object in every iteration. For large inputs, this is a performance bottleneck.
    *   **Recommendation**: Collect characters in a list and use `"".join(list)` at the end.

#### 4. RAG Rules Violations

**Deeply Nested Conditional Logic**
*   **Location**: `main()` function.
*   **Issue**: There are four levels of nested `if` statements checking `GLOBAL_CONFIG` and `val`. This increases cognitive load and reduces readability.
*   **Recommendation**: Use guard clauses to flatten the logic. For example:
    ```python
    if not GLOBAL_CONFIG["flag"]:
        print("Flag disabled")
        return

    if val <= 5:
        print("Value too small")
        return
    # ... and so on
    ```

**Magic Numbers**
*   **Location**: `NumberProcessor.process` and `main()`.
*   **Issue**: The numbers `1234`, `5678`, and `9999` are "magic numbers" with no explained purpose.
*   **Recommendation**: Move these to named constants (e.g., `MULTIPLIER`, `MODULUS`, `OFFSET`) to clarify their intent.

**Shared Mutable State**
*   **Location**: `GLOBAL_CONFIG`.
*   **Issue**: The use of a global dictionary for configuration introduces hidden coupling. If this dictionary is modified elsewhere in a larger application, it can lead to unpredictable behavior.
*   **Recommendation**: Pass configuration explicitly to the functions or classes that require it.

**Implicit Truthiness**
*   **Location**: `if GLOBAL_CONFIG["flag"]:`
*   **Issue**: While common in Python, the RAG rules suggest explicit comparisons for clarity.
*   **Recommendation**: Use `if GLOBAL_CONFIG["flag"] is True:`.

#### 5. Documentation & Testing
*   **Missing Tests**: There are no unit tests for the `StringProcessor` or `NumberProcessor` logic.
*   **Missing Docstrings**: The classes and methods lack documentation explaining the expected input/output types and the purpose of the transformations.