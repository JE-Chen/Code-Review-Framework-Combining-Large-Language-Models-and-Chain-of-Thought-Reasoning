### Code Smell Type: Global State
**Problem Location:**  
```python
GLOBAL_CACHE = {}
# ... in get_users, get_posts, get_todos
GLOBAL_CACHE["users"] = data
```

**Detailed Explanation:**  
Global state (`GLOBAL_CACHE`) creates tight coupling and hidden dependencies. The cache is mutated as a side effect without being used in any meaningful way (the cached data isn't consumed elsewhere). This violates the principle of least surprise, makes unit testing impossible (since cache state is shared across tests), and introduces non-determinism. If `get_users` is called multiple times, the cache will be overwritten, breaking the expected behavior.

**Improvement Suggestions:**  
Remove the global cache entirely. If caching is needed, implement it as a configurable dependency in `APIClient` (e.g., `APIClient(cache=InMemoryCache())`). If no caching is required, delete the cache-related code. The client should return raw data without side effects.

**Priority Level:** High  

---

### Code Smell Type: Duplicate Code
**Problem Location:**  
```python
def get_users(client):
    data = client.fetch("/users")
    GLOBAL_CACHE["users"] = data
    return data

def get_posts(client):
    data = client.fetch("/posts")
    GLOBAL_CACHE["posts"] = data
    return data

# ... (same pattern for get_todos)
```

**Detailed Explanation:**  
Three nearly identical functions violate DRY (Don't Repeat Yourself). Each function repeats the same pattern of fetching data, caching it, and returning the result. If the caching logic changes (e.g., adding expiration), all three functions must be updated. This increases maintenance cost and the risk of inconsistencies.

**Improvement Suggestions:**  
Replace with a single generic fetcher:  
```python
def fetch_endpoint(client, endpoint):
    data = client.fetch(endpoint)
    return data  # Remove cache dependency
```
Then call it directly:  
```python
users = fetch_endpoint(client, "/users")
posts = fetch_endpoint(client, "/posts")
```
*If caching is required*, add it to `APIClient` as a method (e.g., `client.get_users()`), avoiding global state.

**Priority Level:** High  

---

### Code Smell Type: Overly Broad Exception Handling
**Problem Location:**  
```python
def fetch(self, endpoint):
    try:
        # ...
    except Exception as e:
        return {"error": str(e)}
```

**Detailed Explanation:**  
Catching `Exception` hides critical errors (e.g., `KeyboardInterrupt`, `SystemExit`, or `ConnectionError`). This masks bugs and makes debugging impossible. The error message `str(e)` also leaks implementation details (e.g., `ConnectionError`), which is unhelpful for users.

**Improvement Suggestions:**  
Catch specific exceptions:  
```python
from requests.exceptions import RequestException

def fetch(self, endpoint):
    try:
        # ...
    except RequestException as e:
        return {"error": f"API request failed: {str(e)}"}
```
Add logging for debugging, and consider raising custom exceptions for business logic.

**Priority Level:** High  

---

### Code Smell Type: Magic Numbers
**Problem Location:**  
```python
if len(results) < 5:
    print("Few results")
elif len(results) < 20:
    print("Moderate results")
else:
    print("Too many results")
```

**Detailed Explanation:**  
The numbers `5` and `20` are arbitrary and unexplained. If business rules change, these values must be searched for and updated manually. This reduces readability and increases the risk of bugs (e.g., if `20` should be `25`).

**Improvement Suggestions:**  
Define named constants:  
```python
FEW_RESULTS_LIMIT = 5
MODERATE_RESULTS_LIMIT = 20

# Then:
if len(results) < FEW_RESULTS_LIMIT:
    print("Few results")
elif len(results) < MODERATE_RESULTS_LIMIT:
    print("Moderate results")
```

**Priority Level:** Medium  

---

### Code Smell Type: Lack of Documentation
**Problem Location:**  
No docstrings for `APIClient`, `get_users`, `process_all`, or `main`.

**Detailed Explanation:**  
Missing documentation makes it impossible to understand the purpose of classes, methods, or business logic without reading implementation details. This hinders onboarding, debugging, and maintenance.

**Improvement Suggestions:**  
Add docstrings:  
```python
class APIClient:
    """Handles API requests with configurable base URL."""
    
    def __init__(self, base_url: str):
        """Initialize client with base URL."""
        self.base_url = base_url

def get_users(client: APIClient) -> dict:
    """Fetch user data from /users endpoint."""
    # ...
```

**Priority Level:** Medium  

---

### Code Smell Type: Inconsistent Variable Names
**Problem Location:**  
```python
for u in users:  # "u" is unclear
    if u.get("id") == 1:
        results.append("Special User: " + u.get("name", "Unknown"))

for p in posts:  # "p" is unclear
    if len(p.get("title", "")) > 15:
        results.append("Long Post: " + p["title"])
```

**Detailed Explanation:**  
Short, single-letter variable names (`u`, `p`, `t`) reduce readability. Names like `u` imply "user" but aren’t descriptive enough. This forces readers to mentally map names to context.

**Improvement Suggestions:**  
Use meaningful names:  
```python
for user in users:
    if user.get("id") == 1:
        results.append(f"Special User: {user.get('name', 'Unknown')}")
```

**Priority Level:** Low  

---

### Code Smell Type: String Concatenation in Loops
**Problem Location:**  
```python
results.append("Special User: " + u.get("name", "Unknown"))
```

**Detailed Explanation:**  
String concatenation (`+`) in loops is inefficient (creates temporary strings). While not critical for small datasets, it’s a bad habit that can cause performance issues at scale.

**Improvement Suggestions:**  
Use f-strings or formatted strings:  
```python
results.append(f"Special User: {u.get('name', 'Unknown')}")
```

**Priority Level:** Low