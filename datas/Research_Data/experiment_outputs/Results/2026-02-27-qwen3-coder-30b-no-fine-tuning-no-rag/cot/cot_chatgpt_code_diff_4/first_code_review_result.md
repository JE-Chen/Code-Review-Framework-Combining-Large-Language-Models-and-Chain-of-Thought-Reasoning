### Code Review Summary

#### 1. **Readability & Consistency**
- **Indentation and Formatting**: Indentation is consistent and readable.
- **Comments**: No inline comments; could benefit from docstrings for functions to explain purpose and behavior.

#### 2. **Naming Conventions**
- **Variables/Functions**: 
  - `CONN`, `CURSOR` are acceptable for global DB connection but should ideally be prefixed or named more explicitly (e.g., `DB_CONNECTION`, `DB_CURSOR`).
  - Function names like `do_business_logic_but_sql_heavy()` are not descriptive and don't reflect what they do clearly.
  - Consider renaming `write_log` to something like `insert_log_entry`.

#### 3. **Software Engineering Standards**
- **Modularity**: The code works as a single module, but it’s tightly coupled to SQLite and uses global state (`CONN`, `CURSOR`). This makes testing and reuse difficult.
- **Duplicate Code**: There's no duplication in logic, but repeated SQL string concatenation in `write_log()` can be improved.
- **Refactoring Suggestions**:
  - Move database setup into a class or separate module.
  - Extract SQL queries into constants for better maintainability.

#### 4. **Logic & Correctness**
- **SQL Injection Risk**: Using string formatting (`f"INSERT INTO logs ..."`), which exposes the code to SQL injection vulnerabilities.
- **Commit Handling**: Random commits in `write_log()` may lead to inconsistent data states and hard-to-debug behavior.
- **Exception Handling**: Catching generic exceptions in `do_business_logic_but_sql_heavy()` without logging or re-raising is poor practice.

#### 5. **Performance & Security**
- **Security**: SQL injection is a major concern due to direct string interpolation.
- **Performance**: Repeated commit calls inside loops increase I/O overhead unnecessarily.

#### 6. **Documentation & Testing**
- **Documentation**: Missing docstrings and inline comments make understanding intent harder.
- **Testing**: No unit tests provided — critical for ensuring correctness and preventing regressions.

#### 7. **Suggestions for Improvement**

- ✅ Replace f-string SQL construction with parameterized queries.
- ✅ Rename functions for clarity: e.g., `do_business_logic_but_sql_heavy()` → `simulate_user_activity()`.
- ✅ Use a class-based approach to encapsulate DB logic and avoid global variables.
- ✅ Add docstrings and comments to clarify functionality.
- ⚠️ Avoid catching generic `Exception` — log or re-raise appropriately.
- 🧹 Improve commit strategy: batch operations before committing.
- 🛡️ Add input validation where needed (e.g., message length, limit values).

---

Let me know if you'd like help implementing these changes!