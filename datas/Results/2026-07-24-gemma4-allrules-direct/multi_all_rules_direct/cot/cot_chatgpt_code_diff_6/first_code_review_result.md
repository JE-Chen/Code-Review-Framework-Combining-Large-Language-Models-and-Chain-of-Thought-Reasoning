### Code Review

**Naming Conventions**
* `get_something` and `do_network_logic` are vague. Use more descriptive names that reflect the actual purpose of the functions (e.g., `fetch_data` and `execute_fetch_cycle`).

**Logic & Correctness**
* **Inconsistent Return Types:** `parse_response` returns a dictionary on HTTP error, a string on JSON parsing failure, and a formatted string on success. This forces the caller to handle multiple types, increasing the risk of runtime errors.
* **Missing Timeout:** The `else` branch in `get_something` calls `SESSION.get(url)` without a timeout. This can lead to the application hanging indefinitely if the server does not respond.

**Software Engineering Standards**
* **Broad Exception Handling:** `parse_response` and `main` use `except Exception:`. This hides specific errors (like `JSONDecodeError` or `ConnectionError`) and makes debugging difficult. Catch specific exceptions instead.
* **Shared Mutable State:** `SESSION` is defined as a global variable. While acceptable for simple scripts, it introduces hidden coupling. Consider passing the session as an argument or encapsulating it in a class.

**Performance & Security**
* **URL Construction:** Using string concatenation for query parameters (`"?type=" + kind`) is fragile. Use the `params` argument in `requests.get()` to ensure proper URL encoding.

**Readability & Consistency**
* **Magic Numbers:** The values `0.05` and `0.1` in `do_network_logic` are magic numbers. Define them as named constants (e.g., `MIN_RESPONSE_TIME_THRESHOLD`) to explain their intent.