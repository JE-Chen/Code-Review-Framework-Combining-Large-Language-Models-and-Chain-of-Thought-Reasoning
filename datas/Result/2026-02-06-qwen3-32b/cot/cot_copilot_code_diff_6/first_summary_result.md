# Code Review: bad_requests.py

## 🔴 Critical Issues

- **Global State Abuse**  
  `GLOBAL_SESSION` and `ANOTHER_GLOBAL` create hidden dependencies. This violates modularity and makes testing impossible. Replace with dependency injection.

- **Inadequate Error Handling**  
  `except Exception as e` and `except:` suppress all errors without context. This masks bugs (e.g., network failures) and violates safety principles.

- **Function Overload**  
  `functionThatDoesTooMuchAndIsHardToUnderstand` performs 3 distinct HTTP operations + logging. Splits into single-responsibility functions.

## 🟠 Significant Issues

- **Poor Naming**  
  `weirdVariableName`, `ANOTHER_GLOBAL`, and the function name lack semantic meaning. Names must describe *purpose*, not implementation.

- **Hardcoded URLs**  
  URLs like `https://jsonplaceholder.typicode.com/posts/1` should be configurable or injected to support environment changes.

- **No Logging**  
  `print()` statements are untraceable in production. Use structured logging (e.g., `logging.info()`).

## ✅ Minor Improvements

- **Resource Management**  
  Session (`GLOBAL_SESSION`) is never closed. Add explicit cleanup or use context managers.

- **Redundant Checks**  
  `if r2.status_code == 200` is unnecessary when `r2.text` is used unconditionally.

## 🛠️ Recommendations

1. **Replace globals**  
   Inject session via constructor:  
   ```python
   class HttpClient:
       def __init__(self, session: requests.Session = None):
           self.session = session or requests.Session()
   ```

2. **Split functions**  
   ```python
   def fetch_post(post_id: int) -> dict:
       # Returns parsed response
   ```

3. **Add error context**  
   Instead of `print("Error: ...")`, use:  
   ```python
   logger.error("Failed to fetch post %d", post_id, exc_info=True)
   ```

4. **Remove hardcoded URLs**  
   Externalize endpoints via config (e.g., `config.ENDPOINTS.POSTS`).

## 🌟 Why This Matters

This code is **untestable** (due to globals), **unmaintainable** (single function), and **unreliable** (error suppression). Refactoring enables:
- Unit tests without network calls
- Environment flexibility (dev/staging/prod)
- Clear error diagnostics

---

## Items to Confirm

- [ ] Will dependency injection be applied to all HTTP clients?
- [ ] Are error logs structured for production monitoring?
- [ ] Will session cleanup be handled via context managers?

> ⚠️ **Risk**: Current implementation may cause silent failures in production. Refactor *before* merging.  
> 💡 **Note**: This is a foundational cleanup. Avoid adding new features until the structure is solid.