### Code Review

**Naming Conventions**
* `get_something` and `do_network_logic` are vague. Use more descriptive names (e.g., `fetch_data` and `execute_fetch_cycle`).

**Logic & Correctness**
* **Inconsistent Return Types:** `parse_response` returns a dictionary on HTTP error, a string on JSON failure, and a formatted string on success. This will likely cause `TypeError` or unexpected behavior in the calling function.
* **Unstable Timeout:** `get_something` randomly applies a 1-second timeout or no timeout at all. This creates non-deterministic behavior and potential hangs.
* **Broad Exception Handling:** `except Exception` in `parse_response` and `main` is too broad; it masks specific failures (like `JSONDecodeError` or `ConnectionError`) and makes debugging difficult.

**Software Engineering Standards**
* **URL Construction:** Using string concatenation for query parameters (`"?type=" + kind`) is fragile. Use the `params` argument in `requests.get()` for better encoding and readability.

**Performance & Security**
* **Resource Management:** While `SESSION.close()` is called in `main`, using a `with requests.Session() as session:` block is the standard way to ensure resources are released even if an exception occurs.

**Suggestions for Improvement**
* Standardize the return type of `parse_response` (e.g., always return a string or a consistent Result object).
* Replace string concatenation with `SESSION.get(url, params={"type": kind})`.
* Set a consistent timeout for all network requests.