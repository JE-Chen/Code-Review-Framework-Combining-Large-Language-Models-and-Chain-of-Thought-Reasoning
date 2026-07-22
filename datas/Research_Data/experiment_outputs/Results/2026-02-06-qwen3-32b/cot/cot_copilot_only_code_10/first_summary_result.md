# Code Review

## Readability & Consistency
- ✅ Consistent 4-space indentation and clean formatting.
- ⚠️ Global `GLOBAL_CACHE` introduces hidden state, violating readability principles. Prefer dependency injection over global state.
- ⚠️ `fetch` method uses overly broad exception handling (catches all exceptions).

## Naming Conventions
- ✅ `APIClient`, `get_users`, `process_all` are descriptive.
- ⚠️ `GLOBAL_CACHE` is misleading – cache isn't truly global (only used in `get_*` functions). Should be named `CACHE` or removed entirely.
- ⚠️ `process_all` is vague – consider `aggregate_and_process_data`.

## Software Engineering
- ⚠️ **Critical flaw**: `GLOBAL_CACHE` couples all functions together. Makes code non-reusable, non-testable, and stateful.  
  *Fix:* Remove global cache – manage state via client or pass cache explicitly.
- ⚠️ `get_*` functions mix API fetching and caching responsibilities (violates SRP).
- ⚠️ Hard-coded user ID `1` in `process_all` is fragile.

## Logic & Correctness
- ⚠️ `fetch` returns dictionary on error, but `process_all` assumes list results. Will crash if API returns error.
- ⚠️ No validation for `users`/`posts`/`todos` being lists (fails on API errors).
- ⚠️ `len(p.get("title", "")) > 15` may miss empty titles – use `if "title" in p and len(p["title"]) > 15`.
- ⚠️ Incomplete todos check: `t.get("completed", False)` is safe, but `t.get("title", "No Title")` is redundant.

## Performance & Security
- ⚠️ Global cache grows indefinitely with no eviction strategy (memory leak risk).
- ✅ User-Agent header is properly set.
- ⚠️ No input validation (not applicable here, but good practice).

## Documentation & Testing
- ❌ Missing docstrings for all functions/classes.
- ❌ No unit tests for core logic (e.g., error handling, special-case processing).

---

## Key Recommendations
1. **Remove global cache** – inject cache dependency or eliminate caching entirely.
2. **Split responsibilities** – separate API fetching from caching.
3. **Improve error handling** – raise exceptions for API errors instead of returning error dictionaries.
4. **Avoid hard-coded values** – make user ID configurable.
5. **Add documentation** – docstrings for all public interfaces.
6. **Write tests** – validate edge cases (empty responses, API errors).

## Risk Assessment
- **High risk**: Global cache will cause unexpected behavior in multi-client scenarios.
- **Medium risk**: Hard-coded user ID may break in production.
- **Low risk**: Error handling could cause crashes on API failures.

---

## Items to Confirm
1. Is the global cache intentional? If yes, implement proper cache management.
2. Should user ID `1` be configurable or removed entirely?
3. Are there plans to add unit tests for API error handling?
4. Can we replace `GLOBAL_CACHE` with client-managed state?