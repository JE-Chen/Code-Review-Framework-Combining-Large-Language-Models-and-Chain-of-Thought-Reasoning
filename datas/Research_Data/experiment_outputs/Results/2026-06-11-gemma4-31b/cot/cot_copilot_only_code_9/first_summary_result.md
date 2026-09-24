# Code Review Report

## Overall Assessment
The code implements a basic data retrieval and processing pipeline. However, it suffers from significant architectural issues, including heavy code duplication, poor state management (global variables), and weak error handling. It does not meet professional software engineering standards for maintainability or scalability.

---

## Detailed Feedback

### 1. Readability & Consistency
- **Formatting:** Indentation is consistent, but the `main()` function contains deeply nested `if/else` blocks that reduce readability.
- **Consistency:** The use of `.get()` is inconsistent. In some places, it is used for safety, but in others (e.g., `p["title"]`), direct key access is used, which will cause a `KeyError` if the key is missing.

### 2. Naming Conventions
- **Variable Names:** Names like `u`, `p`, and `c` in loops are too short and non-descriptive. Use `user`, `post`, and `comment` instead.
- **Constants:** `BASE_URL` and `HEADERS` are correctly named as constants.

### 3. Software Engineering Standards
- **Modularity & Duplication:** The functions `get_users`, `get_posts`, and `get_comments` are nearly identical. This violates the DRY (Don't Repeat Yourself) principle.
- **State Management:** The use of `GLOBAL_RESULTS` is a major anti-pattern. Global state makes the code harder to test, prone to side effects, and not thread-safe. Data should be passed via return values.
- **Hardcoding:** The logic for filtering (e.g., `id == 5` or `len > 20`) is hardcoded inside the process function, making it difficult to modify or extend.

### 4. Logic & Correctness
- **Boundary Conditions:** The nested if-statements in `main()` are logically sound but structurally inefficient.
- **Exception Handling:** Using a bare `except Exception` is discouraged. It catches everything (including keyboard interrupts), making debugging difficult. It also lacks a way to signal the caller that a failure occurred beyond returning an empty list.

### 5. Performance & Security
- **Network Efficiency:** The code makes three separate synchronous HTTP requests. While acceptable for this scale, it becomes a bottleneck as more endpoints are added.
- **Resource Management:** The `requests` library is used without a `Session` object, meaning a new TCP connection is established for every call.
- **Input Validation:** There is no validation of the API response status code. `response.json()` will be called even if the server returns a 404 or 500 error, potentially causing a crash.

### 6. Documentation & Testing
- **Documentation:** There are zero docstrings or comments explaining the purpose of the logic or the expected data structures.
- **Testing:** No unit tests are provided. The current structure (global variables) makes writing isolated unit tests nearly impossible.

---

## Recommended Refactoring

```python
import requests
from typing import List, Dict, Any

BASE_URL = "https://jsonplaceholder.typicode.com"
HEADERS = {"Content-Type": "application/json"}

def fetch_resource(endpoint: str) -> List[Dict[str, Any]]:
    """Generic helper to fetch data from the API."""
    try:
        response = requests.get(f"{BASE_URL}/{endpoint}", headers=HEADERS, timeout=10)
        response.raise_for_status() # Check for HTTP errors
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching {endpoint}: {e}")
        return []

def process_data() -> List[str]:
    """Processes users, posts, and comments to extract specific highlights."""
    results = []
    
    # Process Users
    for user in fetch_resource("users"):
        if user.get("id") == 5:
            results.append(f"Special User: {user.get('name', 'Unknown')}")

    # Process Posts
    for post in fetch_resource("posts"):
        title = post.get("title", "")
        if len(title) > 20:
            results.append(f"Long Post Title: {title}")

    # Process Comments
    for comment in fetch_resource("comments"):
        email = comment.get("email", "")
        if "@" in email:
            results.append(f"Comment by email: {email}")
            
    return results

def main():
    results = process_data()
    
    for r in results:
        print(f"Results: {r}")

    count = len(results)
    if count == 0:
        print("No results found")
    elif count < 10:
        print("Few results")
    elif count < 50:
        print("Moderate results")
    else:
        print("Too many results")

if __name__ == "__main__":
    main()
```

## Final Score
| Category | Score (1-5) | Note |
| :--- | :--- | :--- |
| Readability | 3 | Formatting is okay, but nesting is poor. |
| Naming | 2 | Loop variables are too cryptic. |
| Engineering | 1 | Heavy duplication and use of global state. |
| Logic | 3 | Basics work, but error handling is weak. |
| Performance | 2 | Inefficient connection management. |
| Documentation | 1 | No documentation provided. |
| **Total** | **2.0 / 5.0** | **Needs Major Revision** |