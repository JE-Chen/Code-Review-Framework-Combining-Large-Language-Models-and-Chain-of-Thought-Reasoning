### ✅ Pull Request Summary

- **Key Changes**:  
  - Introduces data fetching from a public API (`jsonplaceholder.typicode.com`) for users, posts, and comments.  
  - Processes and filters this data based on specific criteria (user ID, post title length, comment email).  
  - Outputs filtered results along with a count-based status message.

- **Impact Scope**:  
  - Affects all functions in the script (`get_users`, `get_posts`, `get_comments`, `process_data`, `main`).  
  - Uses global variable `GLOBAL_RESULTS` to store output — impacts modularity and testability.

- **Purpose of Changes**:  
  - Demonstrates basic REST API interaction and conditional filtering logic.  
  - Likely intended as a prototype or PoC for data ingestion and processing.

- **Risks and Considerations**:  
  - Global state usage (`GLOBAL_RESULTS`) makes it hard to reuse or parallelize.  
  - Error handling is minimal and lacks structured logging or retry logic.  
  - No input validation or rate limiting considered for external APIs.

- **Items to Confirm**:  
  - Whether global variables are acceptable for this module’s design.  
  - If error handling should be enhanced with retries or custom exceptions.  
  - If tests exist for edge cases like empty responses or invalid JSON.

---

### 📝 Code Review Feedback

#### 1. **Readability & Consistency**
- ✅ Indentation and structure are consistent.
- ⚠️ Inconsistent use of quotes (`""` vs `''`) in string literals.
- ⚠️ Comments are minimal and do not explain *why* certain logic exists.

#### 2. **Naming Conventions**
- ✅ Function names are clear and follow snake_case convention.
- ❌ Global variable name `GLOBAL_RESULTS` does not reflect its purpose clearly.
- 💡 Suggested renaming to `processed_results` or `filtered_output`.

#### 3. **Software Engineering Standards**
- ❌ Duplicated error handling across similar functions (`get_users`, `get_posts`, `get_comments`).
- 💡 Refactor into a generic HTTP fetcher with retry and logging support.
- ❌ Use of global state undermines testability and scalability.
- 💡 Return values instead of mutating shared state.

#### 4. **Logic & Correctness**
- ⚠️ Lack of explicit handling for missing keys or malformed JSON in `response.json()`.
- ⚠️ Magic number `5` used in user filter — should be configurable or documented.
- ⚠️ Nested `if` blocks in result classification can be simplified using match-case or helper functions.

#### 5. **Performance & Security**
- ⚠️ No timeout set on `requests.get()` — could lead to hanging calls.
- ⚠️ No authentication or rate-limiting applied to API calls.
- ⚠️ Potential DoS risk due to unbounded list growth (`GLOBAL_RESULTS`).

#### 6. **Documentation & Testing**
- ❌ Missing docstrings or inline comments explaining business rules.
- ❌ No unit tests provided — difficult to verify behavior under failure scenarios.
- 💡 Add parameterized tests covering normal, edge, and error cases.

#### 7. **Scoring & Feedback Style**
- Balanced feedback prioritizes actionable improvements without overloading details.
- Emphasis on reusability and correctness aligns well with software engineering best practices.

--- 

### 🔧 Recommendations
1. Replace global variable with return value from `process_data`.
2. Extract common patterns into reusable utility functions.
3. Improve error handling with structured logs and timeouts.
4. Add docstrings and unit tests.
5. Avoid magic numbers and hard-coded thresholds where possible.