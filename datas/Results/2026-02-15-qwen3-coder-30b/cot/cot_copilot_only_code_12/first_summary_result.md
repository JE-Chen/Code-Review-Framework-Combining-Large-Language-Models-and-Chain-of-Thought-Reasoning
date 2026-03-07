### 📌 Pull Request Summary

- **Key Changes**  
  - Added basic data generation using `pandas` and random values.
  - Implemented statistical calculations for numeric columns (`A`, `B`) and dummy logic for categorical column (`C`).
  - Included plotting functionality for one column.

- **Impact Scope**  
  - Core module: `main.py` (single-file script with global state usage).
  - Functions affected: `loadData`, `calcStats`, `plotData`, `main`.

- **Purpose of Changes**  
  - Introduce initial framework for generating synthetic data and performing basic analysis.
  - Serve as a prototype or starting point for more complex analytics pipelines.

- **Risks and Considerations**  
  - Heavy reliance on global variables (`DATAFRAME`, `resultList`, `tempStorage`) reduces modularity and testability.
  - No input validation or error handling.
  - Plotting uses default backend which may fail in headless environments.

- **Items to Confirm**  
  - Whether global state is intentional or should be refactored into parameters/classes.
  - If all logic paths (especially edge cases) are covered.
  - Testing strategy for both calculation and visualization components.

---

### ✅ Code Review Feedback

#### 1. Readability & Consistency
- ❌ Inconsistent naming: e.g., `DATAFRAME`, `resultList`, `tempStorage` use mixed case styles.
- ⚠️ Lack of docstrings or inline comments makes intent unclear.
- 🧹 Formatting is inconsistent; consider applying auto-formatters like Black.

#### 2. Naming Conventions
- ❌ Variables like `DATAFRAME`, `resultList`, and `tempStorage` do not follow PEP8 naming standards.
  - Use snake_case for variables: `dataframe`, `result_list`, `temp_storage`.
- ⚠️ Function name `calcStats()` could be clearer: `calculate_statistics()` improves readability.

#### 3. Software Engineering Standards
- ⚠️ Overuse of global variables makes functions tightly coupled and hard to test independently.
- 💡 Extract `calcStats()` logic into reusable helper functions.
- 🛑 Duplicated computation (`st.mean(DATAFRAME[col])`) unnecessarily repeated.

#### 4. Logic & Correctness
- ⚠️ Hardcoded column names ("A", "B") reduce flexibility.
- ❌ No checks for empty or invalid inputs in `DATAFRAME`.
- ⚠️ Redundant stats added (e.g., `meanA_again`), potentially confusing behavior.

#### 5. Performance & Security
- ⚠️ Using `matplotlib.pyplot.show()` inside a function may block execution or fail in non-GUI contexts.
- ⚠️ No limits on data size; large datasets could cause performance issues.
- 🔐 No sanitization or validation of generated data before processing.

#### 6. Documentation & Testing
- ❌ Missing docstrings or type hints.
- 🧪 No unit tests provided for any functionality — critical for correctness verification.

#### 7. Recommendations
- Refactor global state into arguments or class-based design.
- Add defensive programming practices (input validation, error handling).
- Improve testability by separating concerns and minimizing side effects.
- Enhance comments and add minimal documentation for future developers.

--- 

### 🎯 Overall Score: ⭐ 3/5  
> Needs improvement in structure, modularity, and clarity. Suitable as a draft but requires major refactor before production readiness.