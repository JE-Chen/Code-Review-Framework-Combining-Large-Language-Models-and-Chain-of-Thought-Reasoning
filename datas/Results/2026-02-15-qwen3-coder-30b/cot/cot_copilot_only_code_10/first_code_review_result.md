### Code Review Summary

#### 1. **Readability & Consistency**
- Indentation and structure are consistent but could benefit from more descriptive comments.
- Missing docstrings or inline comments for functions and classes.

#### 2. **Naming Conventions**
- Variables like `u`, `p`, `t` are too generic; use more descriptive names.
- Global constants (`BASE_URL`, `GLOBAL_CACHE`) are acceptable but can be improved by encapsulation.

#### 3. **Software Engineering Standards**
- Duplicated logic in `get_users`, `get_posts`, and `get_todos`.
- No clear separation between API fetching and business logic.
- Lack of error handling for missing keys in fetched data.

#### 4. **Logic & Correctness**
- Redundant conditionals in `main()` (nested if statements).
- Potential runtime exceptions when accessing nested dictionaries without safety checks.

#### 5. **Performance & Security**
- Global cache may cause concurrency issues in multi-threaded environments.
- Hardcoded endpoints and headers make it less flexible or secure.

#### 6. **Documentation & Testing**
- No inline documentation or docstrings.
- No unit tests provided for core functionality.

---

### Suggested Improvements

- **Refactor duplicate methods**: Extract common logic into reusable helper functions.
- **Use descriptive variable names**: Replace `u`, `p`, `t` with `user`, `post`, `todo`.
- **Improve control flow**: Simplify nested conditionals in `main()`.
- **Add defensive programming practices**: Handle missing keys gracefully.
- **Consider thread safety**: Avoid modifying shared state (`GLOBAL_CACHE`) without locking mechanisms.
- **Add documentation and tests** to improve maintainability and reliability.