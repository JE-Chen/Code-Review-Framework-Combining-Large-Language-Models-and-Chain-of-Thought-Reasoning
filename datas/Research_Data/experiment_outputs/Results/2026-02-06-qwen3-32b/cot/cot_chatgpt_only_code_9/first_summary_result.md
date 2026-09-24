### Code Review

#### Readability & Consistency
- **Consistent style**: Indentation and naming follow Python conventions.
- **Critical gaps**: Missing docstrings, inline comments, and API usage context. Example: `GLOBAL_CACHE` usage lacks rationale.
- **Global state**: Overuse of module-level globals (`SESSION`, `GLOBAL_CACHE`) violates encapsulation.

#### Naming Conventions
- **Good**: `APIClient`, `fetch`, `process_all` are descriptive.
- **Problematic**: 
  - `GLOBAL_CACHE` implies immutability but is mutable and shared.
  - Hardcoded `id=1` in `process_all` lacks context (why user ID 1?).

#### Software Engineering Standards
- **Critical duplication**: `get_users`, `get_posts`, `get_todos` are nearly identical. Refactor to avoid code repetition.
- **Broken encapsulation**: 
  - `APIClient` relies on global `SESSION` instead of managing its own session.
  - `GLOBAL_CACHE` couples API logic to global state.
- **Testability**: Global state and hardcoded values make unit testing impossible.

#### Logic & Correctness
- **Critical bug**: 
  - If API returns an error (e.g., `response.status_code != 200`), `fetch` returns a dict. 
  - `process_all` then tries to iterate over the error dict (e.g., `for u in users`), causing `TypeError`.
- **Overly broad exception handling**: `fetch` catches all exceptions (including `KeyboardInterrupt`), masking unintended errors.
- **Missing edge cases**: 
  - `get_users` assumes `/users` returns a list (no validation).
  - Hardcoded `id=1` ignores potential missing user.

#### Performance & Security
- **No critical issues**: 
  - User-Agent is harmless.
  - No sensitive data exposed.
- **Minor concern**: Global `SESSION` could cause resource leaks if reused across threads (though unlikely in this context).

#### Documentation & Testing
- **Missing**: 
  - No docstrings for classes/functions.
  - Zero unit tests (e.g., mock API responses).
- **Risk**: Without tests, logic errors (like the `TypeError` above) are uncaught.

---

### PR Summary

- **Key changes**: 
  - Removed global cache and duplicated endpoint functions.
  - Added client-managed session and proper error handling.
  - Fixed API error handling in processing logic.
- **Impact scope**: 
  - Modified `APIClient` class and `process_all` logic.
  - Removed `get_*` utility functions.
- **Purpose**: 
  - Eliminate global state and code duplication.
  - Prevent runtime crashes when API returns errors.
- **Risks and considerations**: 
  - Existing callers must use the new `APIClient` pattern.
  - Processing logic now safely skips API errors.
- **Items to confirm**: 
  - Verify `process_all` handles API errors without crashing.
  - Confirm `APIClient` manages its own session correctly.