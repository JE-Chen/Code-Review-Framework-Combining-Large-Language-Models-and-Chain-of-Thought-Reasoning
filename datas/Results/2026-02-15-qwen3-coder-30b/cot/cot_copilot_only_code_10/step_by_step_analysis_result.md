1. **Global Variable Usage (`no-global-variables`)**
   - **Issue**: The code uses a global cache (`GLOBAL_CACHE`) across multiple functions.
   - **Explanation**: Relying on global state makes testing harder and introduces unpredictable side effects.
   - **Why It Happens**: Not designing for dependency injection or modularity.
   - **Impact**: Reduces reusability and makes debugging more complex.
   - **Fix**: Pass the cache as a parameter or inject it via constructor.
     ```python
     def get_users(self, cache=None):
         # ...
     ```

2. **Duplicate Code (`no-duplicate-code`)**
   - **Issue**: Functions `get_users`, `get_posts`, and `get_todos` repeat similar logic.
   - **Explanation**: Identical fetch-and-cache workflows are repeated unnecessarily.
   - **Why It Happens**: Lack of abstraction and shared functionality.
   - **Impact**: Increases maintenance cost and inconsistency risk.
   - **Fix**: Refactor into a generic method like `fetch_and_cache(endpoint)`.
     ```python
     def fetch_and_cache(self, endpoint, cache):
         # Shared logic here
     ```

3. **Generic Exception Handling (`no-implicit-exception-handling`)**
   - **Issue**: Catches all exceptions (`except Exception:`).
   - **Explanation**: Masks real bugs and prevents meaningful error recovery.
   - **Why It Happens**: Overuse of broad exception catching.
   - **Impact**: Decreases reliability and debuggability.
   - **Fix**: Handle specific exceptions instead.
     ```python
     except requests.RequestException as e:
         # Handle only known HTTP-related errors
     ```

4. **Resource Leak Risk (`no-uncontrolled-resource-usage`)**
   - **Issue**: A global session object isn’t managed properly.
   - **Explanation**: Sessions can accumulate resources over time if not closed.
   - **Why It Happens**: Ignoring lifecycle management.
   - **Impact**: Potential memory leaks in long-running systems.
   - **Fix**: Use context managers or explicit cleanup.
     ```python
     with requests.Session() as session:
         # Use session
     ```

5. **Hardcoded URLs (`no-hardcoded-values`)**
   - **Issue**: Endpoints like `/users`, `/posts` are hardcoded.
   - **Explanation**: Makes it hard to change or configure without modifying source code.
   - **Why It Happens**: Lack of configuration abstraction.
   - **Impact**: Reduces flexibility and scalability.
   - **Fix**: Move endpoints to constants or config files.
     ```python
     USERS_ENDPOINT = "/users"
     ```

6. **Magic Numbers (`no-magic-numbers`)**
   - **Issue**: Thresholds like `5` and `20` appear without context.
   - **Explanation**: Readers cannot easily infer their meaning or purpose.
   - **Why It Happens**: No naming or documentation for values.
   - **Impact**: Makes future changes fragile and unclear.
   - **Fix**: Define named constants.
     ```python
     FEW_RESULTS_THRESHOLD = 5
     MAX_TITLE_LENGTH = 15
     ```

7. **Missing Documentation (`no-bad-comments`)**
   - **Issue**: Functions lack docstrings or inline comments.
   - **Explanation**: Other developers struggle to understand behavior.
   - **Why It Happens**: Neglecting good practices during development.
   - **Impact**: Slows down collaboration and knowledge transfer.
   - **Fix**: Add clear docstrings and explain edge cases.
     ```python
     def get_users():
         """Fetches users from API."""
         pass
     ```

---

### Summary of Key Principles to Apply:
- **Dependency Injection**: Avoid global state; pass dependencies explicitly.
- **DRY Principle**: Extract repeated logic into reusable components.
- **Specific Exceptions**: Catch only expected failures.
- **Configuration Management**: Externalize hard-coded values.
- **Naming Consistency**: Stick to PEP8 style guidelines.
- **Clear Intent**: Use descriptive names and add docs for clarity.