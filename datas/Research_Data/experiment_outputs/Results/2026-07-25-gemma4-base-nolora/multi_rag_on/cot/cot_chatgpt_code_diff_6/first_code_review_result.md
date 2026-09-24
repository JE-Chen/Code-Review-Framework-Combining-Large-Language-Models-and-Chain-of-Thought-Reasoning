### Code Review

**Logic & Correctness**
* **Inconsistent Return Types:** `parse_response` returns a dictionary on HTTP error, a string on JSON parsing failure, and a formatted string on success. This will likely cause `TypeError` or unexpected behavior in the calling function.
* **Unreliable Timeout:** In `get_something`, the `timeout` is applied randomly. This makes the function's behavior non-deterministic and difficult to debug or test.

**Software Engineering Standards**
* **Broad Exception Handling:** `parse_response` and `main` use `except Exception:`. This violates the rule against catching broad exceptions and can hide critical bugs (e.g., `KeyboardInterrupt` or `MemoryError`).
* **Shared Mutable State:** `SESSION` is defined as a global module-level object. This introduces hidden coupling and makes unit testing difficult. It should be passed as an argument or encapsulated in a class.

**Naming Conventions**
* **Vague Naming:** `get_something` and `do_network_logic` are non-descriptive. Use names that reflect the actual purpose (e.g., `fetch_data` and `execute_fetch_cycle`).

**Performance & Security**
* **URL Construction:** Using string concatenation for URLs (`BASE_URL + endpoint + ...`) is error-prone. Use `requests`' `params` argument to handle query strings safely and correctly.

**Suggestions for Improvement**
* **Standardize Returns:** Ensure `parse_response` returns a consistent type (e.g., always a string or always a dictionary).
* **Refactor Session:** Move `requests.Session()` into a context manager within `main()` or pass it as a dependency to the functions.
* **Specific Exceptions:** Replace `except Exception:` with specific errors like `requests.exceptions.RequestException` or `ValueError`.
* **Use Params:** Change `SESSION.get(url)` to `SESSION.get(url, params={"type": kind})`.