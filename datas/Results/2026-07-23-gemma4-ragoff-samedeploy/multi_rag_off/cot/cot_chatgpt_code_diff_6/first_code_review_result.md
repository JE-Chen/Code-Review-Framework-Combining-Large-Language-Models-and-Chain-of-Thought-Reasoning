### Code Review: `fetcher.py`

**Naming Conventions**
*   `get_something` and `do_network_logic` are vague. Rename to more descriptive names (e.g., `fetch_data` and `execute_fetch_cycle`) to reflect their actual purpose.

**Logic & Correctness**
*   **Inconsistent Return Types:** `parse_response` returns a dictionary on HTTP error, a string on JSON parsing failure, and a formatted string on success. This will likely cause `TypeError` or unexpected behavior in the calling function. Use a consistent return type or raise specific exceptions.
*   **Unstable Timeout Logic:** `get_something` randomly applies a 1-second timeout or no timeout at all. This creates non-deterministic behavior and makes debugging network issues difficult.
*   **Broad Exception Handling:** `except Exception:` in `parse_response` and `main` catches all errors (including `KeyboardInterrupt` or `SystemExit` in some contexts). Catch specific exceptions (e.g., `requests.exceptions.RequestException`, `ValueError`).

**Software Engineering Standards**
*   **URL Construction:** Using string concatenation for query parameters (`"?type=" + kind`) is error-prone. Use the `params` argument in `requests.get()` for cleaner and safer URL encoding.
*   **Resource Management:** The `SESSION` is closed manually in a `try/except` block. It is more idiomatic and safer to use a `with requests.Session() as session:` context manager.

**Performance & Security**
*   **Lack of Global Timeout:** The branch of `get_something` without a timeout can hang indefinitely if the server does not respond, potentially blocking the entire application.