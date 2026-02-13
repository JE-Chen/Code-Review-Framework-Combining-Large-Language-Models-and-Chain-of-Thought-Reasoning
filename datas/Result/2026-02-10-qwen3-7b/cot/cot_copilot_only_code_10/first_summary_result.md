### PR Summary
- **Key Changes**: Added processing logic to filter and format API responses, and implemented a main function for output.
- **Impact Scope**: Affected `process_all()` and `main()` functions, and global cache usage.
- **Purpose**: Simplify data processing and output formatting.
- **Risks**: Global cache thread safety, incomplete error handling, and lack of logging.
- **Items to Confirm**: Cache consistency, error messages, and logging.
- **High-Level Summary**: Add docstrings, refactor cache, and enhance error handling.

---

### Code Review Details

#### 1. **Readability & Consistency**
- **Indentation**: Consistent with Python standards (4 spaces).
- **Naming**: `SESSION` and `BASE_URL` are uppercase, but should use lowercase with underscores (e.g., `session` and `base_url`).
- **Comments**: Minimal comments; add docstrings for functions.

---

#### 2. **Naming Conventions**
- **Class Name**: `APIClient` is descriptive but could be `ApiService`.
- **Global Cache**: `GLOBAL_CACHE` is a global variable; consider using a class or singleton.

---

#### 3. **Software Engineering Standards**
- **Modularity**: `fetch()`, `get_users()`, etc., are modular but duplicated logic (e.g., `GLOBAL_CACHE` reuse).
- **Refactoring**: Extract `GLOBAL_CACHE` into a class or use a dictionary.
- **Testability**: No test stubs; add unit tests for `fetch()` and `process_all()`.

---

#### 4. **Logic & Correctness**
- **Edge Cases**: Missing checks for empty responses or invalid API calls.
- **Error Handling**: Minimal error messages; improve with `try/except` blocks.
- **Boundary Conditions**: No explicit checks for empty data or invalid IDs.

---

#### 5. **Performance & Security**
- **Performance**: Single session reuse is efficient.
- **Security**: No input validation; e.g., `endpoint` is hardcoded.

---

#### 6. **Documentation & Testing**
- **Docstrings**: Missing for `process_all()` and `main()`.
- **Tests**: No stubs; add tests for API endpoints and output formatting.

---

#### 7. **Scoring & Feedback**
- **Balance**: Concise summary with actionable improvements.
- **Focus**: Prioritize readability, testing, and error handling.

---

### Recommended Fixes
1. **Add Docstrings**: 
   ```python
   def process_all():
       """Process all API data and return formatted results."""
   ```
2. **Refactor Cache**:
   ```python
   class CacheManager:
       @staticmethod
       def get(key):
           # ...
       @staticmethod
       def set(key, value):
           # ...
   ```
3. **Enhance Error Handling**:
   - Add detailed error messages in `fetch()`.
   - Log exceptions with traceback.
4. **Add Tests**:
   - Unit tests for `fetch()` and `process_all()`.

---

### Final Score
- **Readability**: 8/10
- **Consistency**: 7/10
- **Testing**: 6/10
- **Documentation**: 6/10