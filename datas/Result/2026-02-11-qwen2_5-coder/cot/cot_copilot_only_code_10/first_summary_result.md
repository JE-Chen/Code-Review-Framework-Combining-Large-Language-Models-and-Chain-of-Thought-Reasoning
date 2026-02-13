## PR Summary Template

### Key Changes
- Refactored API client to use session for consistent headers.
- Added caching mechanism to store fetched data globally.
- Created functions `get_users`, `get_posts`, and `get_todos` to encapsulate data fetching.
- Implemented logic to process all data and generate results based on certain criteria.

### Impact Scope
- Modules impacted: `APIClient`, `get_users`, `get_posts`, `get_todos`, `process_all`.
- Files impacted: Single Python file.

### Purpose of Changes
- To improve code modularity, readability, and performance by reducing redundancy and centralizing data fetching logic.
- To enhance usability by providing a clear structure for processing and displaying results.

### Risks and Considerations
- Potential impact on existing cache invalidation mechanisms if they rely on global state.
- Need to ensure thread safety when accessing and modifying `GLOBAL_CACHE`.

### Items to Confirm
- Validate that caching works as expected across multiple calls.
- Confirm that the classification logic in `process_all` is correct and covers edge cases.
- Check if any sensitive information is inadvertently exposed in logs or output.

---

## Code Diff to Review

```python
import requests

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "CodeSmellBot/1.0"})

BASE_URL = "https://jsonplaceholder.typicode.com"
GLOBAL_CACHE = {}

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def fetch(self, endpoint):
        try:
            url = self.base_url + endpoint
            response = SESSION.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": "Bad status: " + str(response.status_code)}
        except Exception as e:
            return {"error": str(e)}

def get_users(client):
    data = client.fetch("/users")
    GLOBAL_CACHE["users"] = data
    return data

def get_posts(client):
    data = client.fetch("/posts")
    GLOBAL_CACHE["posts"] = data
    return data

def get_todos(client):
    data = client.fetch("/todos")
    GLOBAL_CACHE["todos"] = data
    return data

def process_all():
    client = APIClient(BASE_URL)
    users = get_users(client)
    posts = get_posts(client)
    todos = get_todos(client)

    results = []
    for u in users:
        if u.get("id") == 1:
            results.append("Special User: " + u.get("name", "Unknown"))

    for p in posts:
        if len(p.get("title", "")) > 15:
            results.append("Long Post: " + p["title"])

    for t in todos:
        if not t.get("completed", False):
            results.append("Incomplete Todo: " + t.get("title", "No Title"))

    return results

def main():
    results = process_all()
    for r in results:
        print("Result:", r)

    if len(results) > 0:
        if len(results) < 5:
            print("Few results")
        else:
            if len(results) < 20:
                print("Moderate results")
            else:
                print("Too many results")
    else:
        print("No results found")

if __name__ == "__main__":
    main()
```

---