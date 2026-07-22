Overall, the code is functional and easy to read, but it contains several critical architectural flaws—most notably regarding memory management and mutable default arguments—that would cause bugs in a production environment.

### 1. Linter & Python Best Practices

*   **Mutable Default Arguments:** 
    *   **Issue:** `def fetch_resource(url, headers={}, ...)`
    *   **Why it matters:** In Python, default dictionaries are created once at definition time, not at call time. If you modify `headers` inside the function, those changes persist across all future calls to the function.
    *   **Fix:** Use `headers=None` and initialize inside: `headers = headers or {}`.
*   **Shadowing Built-ins:**
    *   **Issue:** `def hash(text):`
    *   **Why it matters:** `hash()` is a built-in Python function. Overriding it can lead to confusing bugs and makes the code less maintainable.
    *   **Fix:** Rename to `calculate_checksum()` or `get_md5()`.
*   **String Concatenation in Loops:**
    *   **Issue:** `line = r["url"] + " | " + ...` in `print_summary`.
    *   **Why it matters:** Repeated string concatenation using `+` is inefficient in Python.
    *   **Fix:** Use f-strings: `f"{r['url']} | {r['status']} | ..."`

### 2. Code Smells

*   **Function-Level State (The "Poor Man's Cache"):**
    *   **Issue:** `fetch_resource.cache = {}`
    *   **Why it matters:** Attaching data to a function object is an unconventional pattern that makes testing and clearing the cache difficult. It also makes the function non-thread-safe.
    *   **Fix:** Use a class to encapsulate the session and cache, or use `functools.lru_cache`.
*   **Inefficient File Downloading:**
    *   **Issue:** `content = b""` followed by `content += chunk` in `download_file`.
    *   **Why it matters:** This loads the entire file into RAM before writing to disk. If you download a 2GB file, the program will crash with an `MemoryError`.
    *   **Fix:** Write chunks directly to the file: `f.write(chunk)`.
*   **Hardcoded Magic Numbers:**
    *   **Issue:** `chunk_size=1234` and `len(content) > 3000`.
    *   **Why it matters:** These numbers are arbitrary and lack context.
    *   **Fix:** Define these as constants at the top of the file (e.g., `CHUNK_SIZE = 1024`).

### 3. Architectural Improvements

*   **Request Session Management:**
    *   **Issue:** Every call to `requests.get` opens and closes a new TCP connection.
    *   **Why it matters:** This is significantly slower for batch operations.
    *   **Fix:** Use `requests.Session()` to reuse connections (Keep-Alive).
*   **Lack of Error Handling:**
    *   **Issue:** No `try...except` blocks around network calls.
    *   **Why it matters:** A single DNS failure or timeout will crash the entire batch process.
    *   **Fix:** Wrap requests in a try-except block and use `r.raise_for_status()`.

---

### Suggested Refactoring (Partial)

```python
import requests
import hashlib
import time

# Use a class to manage state and sessions
class ResourceFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.cache = {}

    def fetch(self, url, headers=None, use_cache=True, allow_redirect=True):
        headers = headers or {}
        if use_cache and url in self.cache:
            return self.cache[url]

        headers["User-Agent"] = "BadClient/1.0"
        
        try:
            r = self.session.get(url, headers=headers, allow_redirects=allow_redirect, timeout=10)
            r.raise_for_status()
            if use_cache:
                self.cache[url] = r
            return r
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

def calculate_md5(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()

def download_file(url, path, preview=False):
    # Stream directly to disk to save memory
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if preview and f.tell() > 3000:
                    break
                f.write(chunk)
    return path
```

### Summary of Strengths
*   **Clear Logic:** The flow of the program is easy to follow.
*   **Good API usage:** Correct use of `stream=True` for downloads and `iter_content` for memory efficiency (though undermined by the `content += chunk` logic).
*   **Modular:** Functions are broken down by responsibility.