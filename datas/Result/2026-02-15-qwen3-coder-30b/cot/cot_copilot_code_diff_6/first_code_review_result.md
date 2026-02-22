### Code Review Summary

- **Readability & Consistency**: Indentation is correct but lacks consistent formatting and comments.
- **Naming Conventions**: Function and variable names are unclear and not descriptive.
- **Software Engineering Standards**: Violates modularity and reusability by using globals and doing too much in one function.
- **Logic & Correctness**: Poor error handling and no return values; logic may silently fail.
- **Performance & Security**: No input validation or session cleanup; global state introduces risk.
- **Documentation & Testing**: Missing docstrings and no tests.

---

### Suggestions

- ✅ **Refactor `functionThatDoesTooMuchAndIsHardToUnderstand`** into smaller, focused functions.
- ✅ **Avoid global variables** like `GLOBAL_SESSION` and `ANOTHER_GLOBAL`; pass dependencies explicitly.
- ✅ **Use descriptive names** such as `fetch_post`, `handle_response`, etc., instead of vague ones.
- ✅ **Replace bare `except:` blocks** with specific exception types for better debugging.
- ✅ **Return results or raise exceptions** instead of printing silently.
- ✅ **Add logging or proper output handling** for production use.
- ✅ **Include docstrings and unit tests** for maintainability and clarity.

--- 

### Example Improvements

```python
# Instead of:
def functionThatDoesTooMuchAndIsHardToUnderstand():

# Use:
def fetch_and_process_posts(session: requests.Session):
    """Fetch and log post data from API endpoints."""
```

This improves clarity, testability, and reduces side effects.