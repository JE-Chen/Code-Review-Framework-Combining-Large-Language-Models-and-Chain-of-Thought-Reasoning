### 📋 PR Summary
- **Key Changes**: Core functions for score calculation, filtering, and data processing.
- **Impact Scope**: `calculate_average_scores`, `filter_high_scores`, `process_misc`, and `main` functions.
- **Purpose**: Compute averages, filter scores, and process misc data.
- **Risks**: Edge cases in score thresholds, data validation.
- **Confirm Items**: Function logic correctness, edge case handling, and data consistency.

---

### ✅ Code Review Highlights

#### 1. **Readability & Consistency**
- ✅ Indentation (4 spaces) and formatting are consistent.
- ❌ Sparse comments and lack of docstrings reduce clarity.

#### 2. **Naming Conventions**
- ✅ Function names are descriptive (`calculate_average_scores`).
- ❌ `DATA` as a global variable could be renamed to `constants`.

#### 3. **Software Engineering Standards**
- ✅ Modular functions with single responsibilities.
- ❌ `main()` is long; consider splitting into smaller functions.

#### 4. **Logic & Correctness**
- ✅ `calculate_average_scores` computes average scores correctly.
- ❌ `filter_high_scores` checks for scores > 40 (not 40).
- ❌ `process_misc` mishandles zero or negative values.

#### 5. **Performance & Security**
- ✅ No performance bottlenecks.
- ❌ No input validation for `DATA` values.

#### 6. **Documentation & Testing**
- ❌ No comments or tests provided.

---

### 🛠️ Recommendations
- Add docstrings to functions.
- Refactor `main()` into smaller helper functions.
- Validate edge cases (e.g., zero or negative values).
- Add unit tests for critical paths.