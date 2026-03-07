### 📌 Pull Request Summary

- **Key Changes**  
  Introduces a new GUI module (`gui.py`) using PySide6 to create a basic window with two buttons and a label. The UI responds to button clicks by updating the label text.

- **Impact Scope**  
  Affects only the newly added `gui.py` file. No existing modules or dependencies are impacted.

- **Purpose of Changes**  
  This PR adds a foundational GUI component for future development. It demonstrates a minimal Qt-based interface but lacks structure and scalability.

- **Risks and Considerations**  
  - Global variables used for state management may cause issues in larger applications.
  - Overuse of lambda functions and nested functions reduces readability and testability.
  - The logic inside `veryStrangeFunctionNameThatDoesTooMuch` does too much and violates separation of concerns.
  - Lack of error handling or input validation raises potential runtime issues.

- **Items to Confirm**  
  - Review use of global variables and consider replacing them with class attributes.
  - Evaluate whether `inner()` and `inner2()` are necessary or can be simplified.
  - Confirm if this is intended as a prototype or production-ready code.

---

### 🔍 Code Review Details

#### 1. **Readability & Consistency**
- ✅ Indentation and formatting follow standard Python conventions.
- ⚠️ Comments are missing; no inline documentation or docstrings provided.
- ⚠️ Function name `veryStrangeFunctionNameThatDoesTooMuch` is unclear and does not reflect its behavior.

#### 2. **Naming Conventions**
- ❌ Function name `veryStrangeFunctionNameThatDoesTooMuch` is misleading and violates naming standards (should describe what it does).
- ❌ Global variable usage (`globalLabel`, `anotherGlobal`) makes code harder to reason about and debug.
- 🟡 Class name `MyWeirdWindow` is vague — could be more descriptive like `MainWindow`.

#### 3. **Software Engineering Standards**
- ❌ Violates single responsibility principle — one function handles layout creation, event binding, and state updates.
- ❌ Duplicated lambda assignments (`lbl.setText(...)`) on same signal.
- ❌ Use of nested functions (`inner`, `inner2`) complicates control flow and testing.
- 🟡 No modularity or reusability — hard-coded UI elements make extension difficult.

#### 4. **Logic & Correctness**
- ⚠️ Lambda expressions connected to signals will execute multiple times if triggered more than once.
- ⚠️ Nested function `inner2` overwrites previous label text silently without clear intent.
- ⚠️ No checks for invalid states or edge cases (e.g., null references or concurrent access).

#### 5. **Performance & Security**
- ⚠️ Using global variables increases risk of side effects and conflicts in multi-threaded environments.
- ⚠️ No explicit resource cleanup or memory management practices observed.

#### 6. **Documentation & Testing**
- ❌ Missing any form of documentation (docstrings, comments).
- ❌ No unit or integration tests included for UI interaction or logic verification.

#### 7. **Scoring Overview**

| Category                     | Score (out of 5) | Notes |
|-----------------------------|------------------|-------|
| Readability & Consistency   | 3                | Formatting OK, but lacks comments and clear naming |
| Naming Conventions          | 2                | Misleading names and globals used extensively |
| Software Engineering        | 2                | Violates SRP, poor structure, non-testable |
| Logic & Correctness         | 3                | Some duplication and unclear behavior |
| Performance & Security      | 2                | Risky use of globals and lambdas |
| Documentation & Testing     | 1                | Completely absent |

**Overall Score:** 2/5 – Needs significant improvement before merging.

---

### 💡 Recommendations

1. **Refactor large functions**: Split `veryStrangeFunctionNameThatDoesTooMuch` into smaller, focused methods.
2. **Avoid global variables**: Replace with class-level attributes or pass data explicitly.
3. **Simplify nested functions**: Flatten logic where possible to improve readability.
4. **Add documentation**: Include docstrings for functions and classes.
5. **Implement testing**: Add unit tests for button interactions and state changes.
6. **Use proper naming**: Rename functions and variables to clearly express their purpose.
7. **Improve error handling**: Add safeguards against unexpected inputs or states.