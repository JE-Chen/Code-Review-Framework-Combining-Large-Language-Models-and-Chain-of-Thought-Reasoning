### Code Review Summary

#### 1. **Readability & Consistency**
- Indentation is consistent and readable.
- Formatting is clean but could benefit from spacing around operators and after commas for improved readability.
- Comments are absent; adding inline comments would help explain intent where needed.

#### 2. **Naming Conventions**
- Class name `APIClient` is clear and descriptive.
- Function names like `get_users`, `get_posts`, etc., are descriptive and match their behavior.
- Variables such as `u`, `p`, `t` in loops reduce clarity; prefer full words (`user`, `post`, `todo`) for better understanding.

#### 3. **Software Engineering Standards**
- Duplicated logic exists in `get_*` functions (e.g., fetching and caching). Could be abstracted into a shared helper or method.
- Global cache usage makes code harder to test and reason about due to side effects.
- Lack of modularity in `process_all()` limits reuse and testability.

#### 4. **Logic & Correctness**
- No explicit error handling beyond returning an error dict; consider raising exceptions instead of silent failure.
- The conditional checks inside loop bodies may not scale well or be easily maintainable.
- Potential off-by-one or indexing issues if data structure changes without updating logic.

#### 5. **Performance & Security**
- Use of global variables (`GLOBAL_CACHE`) introduces tight coupling and reduces thread safety.
- Hardcoded endpoints might cause runtime failures if API changes.
- No input sanitization or rate limiting – not critical here but important for real-world applications.

#### 6. **Documentation & Testing**
- Missing docstrings for functions and classes.
- No unit tests provided; testing core behaviors (fetching, filtering) would improve confidence.

#### 7. **Suggestions**
- Replace `u`, `p`, `t` with descriptive loop variables.
- Abstract repeated logic into a common fetch-and-cache utility.
- Move global state into class fields or inject dependencies.
- Add logging or proper exception propagation.
- Introduce unit tests for key components.

---

### Specific Feedback Points

- ❗ Avoid using `GLOBAL_CACHE` — use dependency injection or local storage for better control.
- ⚠️ Duplicate code in `get_users`, `get_posts`, and `get_todos`.
- 💡 Improve variable names (`u`, `p`, `t`) to increase readability.
- 🧼 Consider adding docstrings and comments for clarity.
- 🔍 Evaluate whether all conditionals can be refactored into reusable helpers.