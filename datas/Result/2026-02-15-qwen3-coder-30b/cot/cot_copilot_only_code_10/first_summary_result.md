### ✅ **Pull Request Summary**

- **Key Changes**  
  - Introduced an `APIClient` class for REST API interaction using `requests`.
  - Added functions to fetch users, posts, and todos from a public JSONPlaceholder API.
  - Implemented basic processing logic to filter and categorize fetched data.
  - Added global caching for fetched data and a simple CLI output handler.

- **Impact Scope**  
  - Core module: `APIClient`, `get_*` functions, and `process_all`.
  - Global state: Uses a shared `GLOBAL_CACHE` dict.
  - Side effects: Prints output directly to stdout in `main`.

- **Purpose of Changes**  
  - Demonstrate a minimal REST client and data processing workflow.
  - Provide a starting point for fetching and filtering external data.

- **Risks and Considerations**  
  - Global cache introduces concurrency issues and makes testing harder.
  - Direct console output reduces reusability.
  - No error recovery or retry logic.
  - Hardcoded API endpoints and logic may not scale.

- **Items to Confirm**  
  - Ensure thread safety for `GLOBAL_CACHE`.
  - Consider decoupling I/O and business logic.
  - Validate caching behavior and memory usage.
  - Confirm test coverage for edge cases (empty responses, timeouts).

---

### 🧠 **Code Review Details**

#### 1. **Readability & Consistency**
- ✅ Indentation is consistent.
- ❌ Comments are missing. Could benefit from docstrings for public APIs (`APIClient`, `get_*`).
- ⚠️ Formatting uses PEP8 but lacks automatic tooling enforcement (e.g., black, flake8).

#### 2. **Naming Conventions**
- ✅ Function and variable names are reasonably descriptive.
- ⚠️ `GLOBAL_CACHE` could be renamed to indicate its purpose or scope (e.g., `API_RESPONSE_CACHE`).
- 🚫 `process_all()` name doesn’t reflect what it does — consider renaming to `analyze_data()` or similar.

#### 3. **Software Engineering Standards**
- ❌ Duplicated logic in `get_users`, `get_posts`, `get_todos`. Should be abstracted into a generic method.
- ⚠️ Global state via `GLOBAL_CACHE` hinders testability and modularity.
- 🚫 No separation between data fetching and processing logic.

#### 4. **Logic & Correctness**
- ✅ Basic filtering works correctly.
- ⚠️ Hardcoded thresholds (`len(title) > 15`, etc.) reduce flexibility.
- ❌ No handling of invalid or malformed JSON responses.
- ⚠️ No retries or fallbacks on failed requests.

#### 5. **Performance & Security**
- ⚠️ Caching without eviction strategy can lead to memory leaks.
- ❌ No rate limiting or backoff on retries.
- ⚠️ No validation of inputs like `endpoint` or `response`.

#### 6. **Documentation & Testing**
- ❌ Missing docstrings and inline comments.
- ⚠️ No unit tests provided. Suggest adding mocks for `requests.Session`.
- 📌 Consider writing test cases for each `get_*` function and edge case (e.g., bad status codes).

#### 7. **Scoring Overview**
| Category             | Score |
|----------------------|-------|
| Readability          | ⭐⭐⭐☆☆ |
| Maintainability      | ⭐⭐☆☆☆ |
| Testability          | ⭐⭐☆☆☆ |
| Performance & Safety | ⭐⭐☆☆☆ |
| Overall              | ⭐⭐☆☆☆ |

---

### 💡 Suggestions for Improvement

1. **Refactor duplicate logic**: Create a common method for fetching resources.
2. **Avoid global variables**: Pass cache or use dependency injection instead.
3. **Add logging or proper output handling**: Instead of direct prints.
4. **Improve error handling**: Add timeout, retry, and response validation.
5. **Introduce unit tests**: Mock session calls to isolate behavior.

---

### 🛠 Example Refactor Snippet

```python
def fetch_resource(client, endpoint):
    response = client.fetch(endpoint)
    if "error" not in response:
        GLOBAL_CACHE[endpoint] = response
    return response
```

This would help reduce redundancy and improve readability.

Let me know if you'd like a full refactor example!