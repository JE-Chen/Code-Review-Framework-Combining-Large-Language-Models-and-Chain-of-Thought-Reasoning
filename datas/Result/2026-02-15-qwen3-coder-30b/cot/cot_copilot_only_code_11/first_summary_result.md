### 📌 Pull Request Summary

- **Key Changes**  
  - Introduced core logic functions (`calculate_average_scores`, `filter_high_scores`, `process_misc`) to analyze data from a static dataset.
  - Added conditional execution based on configuration flags and modes.

- **Impact Scope**  
  - Affects processing of user data and configuration values in a single script file.
  - No external dependencies or integrations impacted.

- **Purpose**  
  - Demonstrates basic data transformation and filtering logic using hardcoded sample data.
  - Serves as a foundation for future enhancements or modularization.

- **Risks & Considerations**  
  - Hardcoded dataset limits scalability and testability.
  - Nested conditionals may reduce readability and increase maintenance risk.
  - No error handling or edge-case checks for invalid inputs or unexpected structures.

- **Items to Confirm**  
  - Whether the use of global `DATA` is intentional or should be passed as parameters.
  - If additional test coverage is required for logic branches.
  - Clarification on expected behavior when config flags are not aligned with logic flow.

---

### ✅ Code Review Feedback

#### 1. **Readability & Consistency**
- **Issue**: Indentation is inconsistent in nested `if` blocks.
- **Suggestion**: Use consistent spacing and consider extracting deeply nested logic into helper functions.

#### 2. **Naming Conventions**
- **Issue**: Generic variable names like `s`, `total`, and `result`.
- **Suggestion**: Replace with more descriptive names such as `score`, `running_total`, and `output`.

#### 3. **Software Engineering Standards**
- **Issue**: Global state dependency via `DATA`.
- **Suggestion**: Pass data as arguments instead of relying on global variables for better modularity and testability.

#### 4. **Logic & Correctness**
- **Issue**: Potential division-by-zero in average calculation if `scores` list is empty.
- **Suggestion**: Add guard clause to check length before dividing.

- **Issue**: Complex nested `if-else` blocks in `main()` logic.
- **Suggestion**: Refactor into named conditional branches or early returns for improved clarity.

#### 5. **Performance & Security**
- **No Major Issues Detected**
  - No known performance bottlenecks or security vulnerabilities in current scope.

#### 6. **Documentation & Testing**
- **Issue**: Missing docstrings and inline comments explaining intent.
- **Suggestion**: Add brief docstrings to clarify purpose and parameter expectations.

- **Issue**: No unit tests provided.
- **Suggestion**: Include unit tests covering different branches of control flow and edge cases.

#### 7. **Scoring & Feedback Style**
- Overall score: ⭐️⭐️⭐️⭐️☆ (4/5) — Good structure but room for improvement in maintainability and robustness.

--- 

### 💡 Recommendations
- Modularize logic into reusable components.
- Introduce parameterized input instead of global constants.
- Improve naming consistency and add defensive checks where applicable.
- Expand test coverage to ensure correctness under various scenarios.