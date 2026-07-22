### Code Review

**Naming Conventions**
* `get_something` and `do_network_logic` are vague. Use more descriptive names (e.g., `fetch_data` and `execute_fetch_cycle`) to reflect their actual purpose.

**Logic & Correctness**
* **Inconsistent Return Types:** `parse_response` returns a dictionary on HTTP error, a string on JSON parsing failure, and a formatted string on success. This will likely cause `TypeError` or unexpected behavior in the calling function.
* **Unstable Timeouts:** `get_something` randomly applies a 1-second timeout or no timeout at all. This creates non-deterministic behavior and potential hangs in production.
* **Broad Exception Handling:** `except Exception` in `parse_response` and `main` is too broad. Catch specific exceptions (e.g., `requests.exceptions.RequestException`, `ValueError`) to avoid masking unrelated bugs.

**Software Engineering Standards**
* **URL Construction:** Using string concatenation for query parameters (`"?type=" + kind`) is error-prone. Use the `params` argument in `requests.get()` for proper encoding.
* **Resource Management:** The `SESSION` is closed manually in a `try/except` block. Using a context manager (`with requests.Session() as session:`) is the standard way to ensure resources are released.

**Performance & Security**
* **Lack of Retries:** The code handles network failures by returning an error status or crashing, but lacks a retry mechanism for transient network issues.