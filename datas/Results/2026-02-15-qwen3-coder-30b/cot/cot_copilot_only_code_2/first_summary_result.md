### ✅ Pull Request Summary

- **Key Changes**  
  - Introduced `BaseProcessor`, `StringProcessor`, and `NumberProcessor` classes for modular data transformation.
  - Added `DataPipeline` to chain processors.
  - Implemented conditional logic based on `GLOBAL_CONFIG`.

- **Impact Scope**  
  - Affects processing pipeline behavior for strings and numbers.
  - Global configuration influences control flow and output messages.

- **Purpose of Changes**  
  - Demonstrates extensible processing framework using inheritance and composition.
  - Adds conditional execution paths based on global settings.

- **Risks and Considerations**  
  - Hardcoded values and nested conditionals may reduce readability and testability.
  - Lack of input validation or error handling could cause runtime issues.

- **Items to Confirm**  
  - Ensure all branches in nested `if` statements are covered by tests.
  - Evaluate whether `GLOBAL_CONFIG` should be injected instead of hardcoded.
  - Verify correctness of string-to-ASCII conversion and number transformation logic.

---

### 🧠 Code Review Feedback

#### 1. **Readability & Consistency**
- Indentation is consistent but could benefit from clearer structure in deeply nested blocks.
- Comments are minimal; consider adding docstrings to clarify purpose of each processor.

#### 2. **Naming Conventions**
- Class and method names are clear and follow standard Python naming conventions (`PascalCase`, `snake_case`).
- No major naming issues detected.

#### 3. **Software Engineering Standards**
- Modular design via inheritance and composition is good.
- Potential duplication in conditional checks (e.g., repeated use of `GLOBAL_CONFIG`) can be abstracted into helper functions.

#### 4. **Logic & Correctness**
- Logic seems correct for intended transformations.
- Edge cases like empty strings or non-numeric inputs may not be fully handled.
- Nested conditionals increase complexity and risk of oversight during maintenance.

#### 5. **Performance & Security**
- No obvious performance bottlenecks.
- No user input is processed directly — low risk of injection or DoS attacks.

#### 6. **Documentation & Testing**
- Missing inline documentation or type hints.
- No unit tests provided for core logic or edge cases.
- Suggestion: Add assertions or test cases covering various inputs and configurations.

#### 7. **Scoring & Feedback Style**
- Concise yet comprehensive feedback focused on key improvements.
- Prioritizes maintainability and clarity over minor stylistic concerns.

---

### 💡 Suggestions for Improvement

- Refactor deeply nested `if` blocks into early returns or helper methods.
- Introduce logging or validation where applicable.
- Add docstrings and type hints for better IDE support and clarity.
- Consider injecting `GLOBAL_CONFIG` rather than relying on global state.

--- 

### 🔚 Final Note
This implementation provides a functional foundation for data transformation pipelines. With minor enhancements for clarity, robustness, and test coverage, it can become more production-ready.