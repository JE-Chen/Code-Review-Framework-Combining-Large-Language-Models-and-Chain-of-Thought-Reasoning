### 🔍 Pull Request Summary

- **Key Changes**: Introduced a new `fetcher.py` module that performs HTTP GET requests using a shared session, parses responses, and logs output. Includes randomized behavior for endpoint types and request delays.
- **Impact Scope**: Affects only the newly added `fetcher.py` file; no existing modules impacted.
- **Purpose**: Demonstrates basic network interaction and parsing logic for external API calls.
- **Risks & Considerations**:
  - Randomized behaviors may make testing unpredictable.
  - Error handling is minimal and could mask issues.
  - Use of `time.sleep()` without coordination can block execution.
- **Items to Confirm**:
  - Whether randomness is intentional or should be controlled via config.
  - If `SESSION.close()` is required or can be omitted safely.
  - Whether error messages like `"not json but who cares"` are acceptable in production.

---

### ✅ Code Review Findings

#### 1. 🧼 Readability & Consistency
- **Issue**: Inconsistent use of spacing around operators (`+`, `=`) and lack of blank lines between logical blocks.
- **Suggestion**: Standardize formatting with black or autopep8 to improve consistency.

#### 2. 🏷️ Naming Conventions
- **Issue**: Function names like `get_something`, `parse_response`, and `do_network_logic` are vague and not very descriptive.
- **Suggestion**: Rename functions to reflect their specific purpose more clearly (e.g., `fetch_endpoint`, `process_api_response`, `execute_fetch_sequence`).

#### 3. 💡 Software Engineering Standards
- **Issue**: Hardcoded values such as `BASE_URL` and `timeout=1` reduce flexibility.
- **Suggestion**: Externalize configuration into environment variables or config files.

#### 4. ⚠️ Logic & Correctness
- **Issue**: Exception handling in `parse_response` silently ignores JSON decode errors.
- **Suggestion**: Log unexpected JSON failures or raise exceptions for better diagnostics.
- **Issue**: Use of `random.choice([True, False])` introduces unpredictability in control flow.
- **Suggestion**: Make this deterministic unless randomness is strictly required.

#### 5. ⚡ Performance & Security
- **Issue**: No retry mechanism or backoff strategy for failed requests.
- **Suggestion**: Add exponential backoff or circuit breaker patterns for robustness.
- **Issue**: Potential DoS through `time.sleep(0.1)` under load.
- **Suggestion**: Avoid sleep unless necessary; consider async or concurrent approaches.

#### 6. 📚 Documentation & Testing
- **Issue**: Missing docstrings or inline comments explaining function roles.
- **Suggestion**: Add docstrings for all public functions to clarify inputs/outputs.
- **Issue**: No unit tests provided.
- **Suggestion**: Include mock-based tests for `get_something` and `parse_response`.

#### 7. 🌟 Overall Suggestions
- **Refactor**: Break logic into smaller reusable components.
- **Test Coverage**: Ensure all branches are covered by unit/integration tests.
- **Security**: Validate input parameters and sanitize outputs before logging or returning them.

---

### 📌 Final Notes
This script works as a proof-of-concept but requires enhancements in design, reliability, and maintainability. Prioritize improving error handling and making behavior predictable before merging into mainline.