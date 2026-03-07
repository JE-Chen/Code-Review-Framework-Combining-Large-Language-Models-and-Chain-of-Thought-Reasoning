# Code Review

## Readability & Consistency
- ✅ Consistent 4-space indentation and formatting throughout.
- ❌ Global variable `GLOBAL_RESULTS` creates hidden dependencies and violates single-responsibility principle.
- ❌ Error handling prints to console instead of using proper logging (e.g., `logging.error`).
- ❌ Inconsistent title handling: `p.get("title", "")` in condition but `p["title"]` in append (risk of KeyError).

## Naming Conventions
- ✅ `BASE_URL`, `HEADERS`, `get_users` are descriptive.
- ❌ `GLOBAL_RESULTS` is misleading (should never be global).
- ❌ Magic number `5` (special user ID) lacks context.
- ❌ `process_data` implies processing but actually mutates global state.

## Software Engineering Standards
- ❌ Critical code duplication in `get_*` functions (90% identical logic).
- ❌ Global state (`GLOBAL_RESULTS`) makes unit testing impossible.
- ❌ No separation of concerns: `process_data` handles both business logic and output.

## Logic & Correctness
- ❌ **Key bug**: `p["title"]` in append risks `KeyError` if title missing (fixed by using `.get` consistently).
- ❌ Special user check (`u.get("id") == 5`) should be configurable.
- ❌ Email validation (`"@" in email`) is insufficient for real email validation.

## Performance & Security
- ✅ No significant performance risks.
- ✅ Fixed URL avoids injection risks.
- ❌ Error handling doesn't distinguish between network failures vs. invalid responses.

## Documentation & Testing
- ❌ Zero docstrings or inline comments explaining *why* logic exists.
- ❌ No unit tests for core logic (e.g., title filtering, email validation).

---

# PR Summary (for Author)

- **Key Changes**:  
  Refactored HTTP functions into a single `fetch_endpoint`, removed global state, added error handling improvements.

- **Impact Scope**:  
  All HTTP-related functions (`get_users`, `get_posts`, `get_comments`), data processing logic, and output handling.

- **Purpose**:  
  Fix global state anti-pattern, eliminate code duplication, and prevent potential `KeyError` in title processing.

- **Risks & Considerations**:  
  - Existing callers of `get_*` functions will now receive `None` on failure instead of empty list (should be safe for current usage).
  - Email validation remains simplistic (requires follow-up for full validation).

- **Items to Confirm**:  
  1. Verify title processing consistently uses `.get("title")` without KeyError.
  2. Confirm special user ID is now configurable (not magic number).
  3. Validate error handling now logs instead of prints.