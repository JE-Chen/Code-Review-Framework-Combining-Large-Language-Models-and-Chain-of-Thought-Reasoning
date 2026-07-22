### Pull Request Summary

- **Key Changes**  
  - Introduced `APIClient` class for making HTTP requests to a REST API.
  - Added functions (`get_users`, `get_posts`, `get_todos`) to fetch and cache data from endpoints.
  - Implemented `process_all()` to analyze fetched data and generate filtered results.
  - Added `main()` function to run the workflow and display output with dynamic messages based on result count.

- **Impact Scope**  
  - Affects the entire module as it defines core logic for fetching, caching, and processing external API data.
  - Uses a global cache (`GLOBAL_CACHE`) which may cause issues in multi-threaded environments or when used in larger systems.

- **Purpose of Changes**  
  - Adds basic functionality to interact with a public JSONPlaceholder API.
  - Demonstrates how to structure an API client and perform simple data processing logic.

- **Risks and Considerations**  
  - Global state via `GLOBAL_CACHE` can lead to concurrency issues and makes testing harder.
  - No error handling for invalid inputs or malformed responses beyond basic HTTP checks.
  - The conditional logic in `main()` could be simplified using a switch-like pattern or mapping.

- **Items to Confirm**  
  - Ensure thread safety if this code will run in concurrent contexts.
  - Validate whether caching behavior is intentional and safe for all use cases.
  - Confirm that no additional validation or sanitization is needed for fetched data before processing.

---

## Code Review

### 1. Readability & Consistency
- ✅ Indentation and formatting are consistent.
- ⚠️ Comments are minimal; consider adding docstrings for classes and functions for better clarity.
- 🧼 Minor formatting improvements like spacing around operators would enhance readability slightly.

### 2. Naming Conventions
- ✅ Function and variable names are descriptive (`fetch`, `get_users`, `process_all`).
- ⚠️ `GLOBAL_CACHE` uses uppercase but doesn't follow typical naming convention for constants (should ideally be `global_cache` or similar).
- 🔁 Class name `APIClient` is appropriate and clear.

### 3. Software Engineering Standards
- ❌ **Global State**: Use of `GLOBAL_CACHE` introduces tight coupling and reduces modularity. This makes the code hard to test and maintain.
- 🔄 **Duplication**: Functions `get_users`, `get_posts`, and `get_todos` have nearly identical logic — they can be refactored into one generic method.
- 🧪 Missing unit tests for any part of the logic — critical for ensuring correctness and preventing regressions.

### 4. Logic & Correctness
- ✅ Basic logic seems correct for fetching data and filtering results.
- ⚠️ Error handling is limited to returning error dictionaries — does not handle malformed JSON or unexpected response structures gracefully.
- ⚠️ Conditional checks like `if u.get("id") == 1:` assume a specific ID value, which might not always be reliable without validation.

### 5. Performance & Security
- ⚠️ Global session usage (`SESSION`) is okay for single-threaded usage but could introduce race conditions in async or threaded applications.
- 🔐 Input validation is missing — raw JSON data from an external source should be validated before use.

### 6. Documentation & Testing
- 📝 Docstrings are absent from functions and classes — adding them improves discoverability and maintainability.
- 🧪 No unit tests provided — especially important for network-dependent and logic-heavy code.

### 7. Final Notes
This code provides a working prototype for interacting with an API and analyzing its data. However, due to global state and lack of abstraction, it's not production-ready. Refactoring to remove global dependencies and adding tests would significantly improve quality.

#### Suggested Improvements:
- Replace `GLOBAL_CACHE` with local or injectable caching mechanism.
- Refactor repeated logic into a common helper function.
- Add docstrings and basic type hints.
- Implement unit tests for core logic and edge cases.
- Consider asynchronous support if scalability becomes an issue.

---