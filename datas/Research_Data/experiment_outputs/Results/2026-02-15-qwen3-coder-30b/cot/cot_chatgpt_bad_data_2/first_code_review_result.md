### Code Review Summary

#### 1. **Readability & Consistency**
- Inconsistent use of blank lines and spacing.
- Comments are missing or minimal; add explanatory comments where needed.
- Indentation is correct but could benefit from consistent formatting (e.g., PEP8-style).

#### 2. **Naming Conventions**
- `users` as a class attribute is ambiguous — consider renaming to reflect its purpose (e.g., `_user_cache`).
- Function names like `process`, `main` are generic and can be more descriptive.
- Use snake_case for functions and variables per Python convention.

#### 3. **Software Engineering Standards**
- Logic duplication exists in `load_users`. Consider abstracting file vs random logic.
- No error propagation or logging when exceptions occur in `_load_from_file`.
- Global config (`CONFIG`) used directly without encapsulation or validation.

#### 4. **Logic & Correctness**
- `process()` does not receive `data` correctly; it's passed by reference but unused properly.
- `result` may be undefined if `CONFIG["retry"] <= 0`.
- Potential race condition due to sleeping in `_load_random_users`.

#### 5. **Performance & Security**
- Unnecessary sleep inside loop in `_load_random_users`.
- No input sanitization or validation for user-provided paths or data.

#### 6. **Documentation & Testing**
- Missing docstrings for classes and methods.
- No unit tests for core functionality.

#### 7. **Suggested Improvements**
- Rename `users` to `_user_cache`.
- Improve error handling in `_load_from_file`.
- Fix argument passing in `process`.
- Add logging or proper exception raising instead of silent failures.
- Move `CONFIG` into a configuration manager or validate before usage.

---

### Specific Feedback Points

- ❌ `except Exception:` should specify types or log errors.
- ⚠️ `process(service)` should pass `data` explicitly.
- 🧠 Consider making `UserService` stateless or using a context manager.
- 💡 Abstract common operations like loading into helper functions.
- ✅ Add docstrings and inline comments for clarity.
- 🛡️ Validate inputs such as `source` and `path`.