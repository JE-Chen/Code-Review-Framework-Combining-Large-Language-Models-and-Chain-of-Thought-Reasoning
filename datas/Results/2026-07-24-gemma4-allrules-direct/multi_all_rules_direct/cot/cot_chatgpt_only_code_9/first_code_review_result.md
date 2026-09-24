### Code Review

**Logic & Correctness**
* **Inconsistent Return Types:** `APIClient.fetch` returns a data object (list/dict) on success but a dictionary with an `"error"` key on failure. This forces callers to check for the existence of an error key before iterating, which is not done in `process_all`, potentially leading to crashes if the API fails.
* **Broad Exception Handling:** `APIClient.fetch` uses `except Exception:`, which hides specific network errors (e.g., timeouts, DNS issues) and makes debugging difficult.

**Software Engineering Standards**
* **Shared Mutable State:** The use of `GLOBAL_CACHE` introduces hidden coupling and makes the code harder to test and reason about. State should be encapsulated within a class or passed explicitly.
* **Code Duplication:** `get_users`, `get_posts`, and `get_todos` are nearly identical. These should be refactored into a single parameterized function (e.g., `fetch_and_cache(client, endpoint)`).
* **Tight Coupling:** `APIClient` relies on a global `SESSION` object rather than managing its own session or accepting one via dependency injection.

**Readability & Naming**
* **Vague Variable Names:** In `process_all`, variables `u`, `p`, and `t` are too short. Use `user`, `post`, and `todo` for better clarity.
* **Deeply Nested Logic:** The `main` function contains deeply nested `if/else` blocks for result counting. This should be refactored using guard clauses or a flatter structure.

**Performance & Security**
* **String Concatenation:** `url = self.base_url + endpoint` is fragile. Use `urllib.parse.urljoin` or f-strings to ensure paths are joined correctly.

**Suggestions for Improvement**
* Refactor `APIClient.fetch` to raise specific exceptions on failure instead of returning error dictionaries.
* Replace `GLOBAL_CACHE` with a local cache object or a class attribute.
* Consolidate the three `get_*` functions into one generic fetcher.
* Flatten the conditional logic in `main()` to improve readability.