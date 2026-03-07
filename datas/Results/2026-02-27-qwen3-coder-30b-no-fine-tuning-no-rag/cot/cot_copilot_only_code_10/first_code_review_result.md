### Code Review Summary

#### 1. **Readability & Consistency**
- **Indentation and Formatting**: Indentation is consistent, but some lines could benefit from better spacing for readability.
- **Comments**: No inline comments are present; adding brief comments to explain key logic would improve clarity.

#### 2. **Naming Conventions**
- **Variable Names**: `u`, `p`, `t` are too generic for loop variables; consider more descriptive names like `user`, `post`, `todo`.
- **Function Names**: Function names (`get_users`, `get_posts`) are clear, but `process_all()` lacks specificity — it's unclear what exactly is being processed.
- **Class Name**: `APIClient` is descriptive and appropriate.

#### 3. **Software Engineering Standards**
- **Duplication**: The repeated pattern in `get_users`, `get_posts`, and `get_todos` can be abstracted into a single reusable function.
- **Global State**: Using `GLOBAL_CACHE` introduces global state which makes testing harder and increases risk of side effects.

#### 4. **Logic & Correctness**
- **Error Handling**: Generic exception handling catches all exceptions without specific logging or re-raising — may hide real issues.
- **Boundary Conditions**: No checks for empty responses or invalid JSON returned by API calls.
- **Logic Flow**: The conditional checks in `process_all()` are valid, but the nested `if` statements in `main()` could be simplified.

#### 5. **Performance & Security**
- **Performance**: Global cache usage may cause concurrency issues if used in multi-threaded environments.
- **Security**: No input sanitization or validation — though this is a simple example, it's worth noting that APIs should validate inputs when applicable.

#### 6. **Documentation & Testing**
- **Documentation**: Missing docstrings for functions and classes.
- **Testing**: No unit tests provided — critical for verifying behavior under various conditions.

#### 7. **Suggestions for Improvement**

- Replace generic variable names (`u`, `p`, `t`) with descriptive ones.
- Refactor repetitive `get_*` functions into one common method.
- Move `GLOBAL_CACHE` into the `APIClient` class to encapsulate caching behavior.
- Add docstrings to functions and class.
- Improve error handling by logging or raising specific exceptions.
- Simplify nested conditionals in `main()` using elif or early returns.
- Consider adding type hints for improved code clarity and maintainability.

--- 

This review focuses on major readability, structure, and maintainability concerns while avoiding overly complex critiques.