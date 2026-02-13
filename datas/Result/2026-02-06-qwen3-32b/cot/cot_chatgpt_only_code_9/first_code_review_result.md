Here's a concise code review focusing on the most critical issues:

- **Global Mutable State**: `GLOBAL_CACHE` is a global dictionary used across functions. This breaks testability and creates hidden dependencies. *Recommendation*: Remove global cache and manage data flow explicitly (e.g., return results from `get_*` functions).

- **Critical Bug in Posts Processing**:  
  `p["title"]` assumes every post has a `title` field. This will crash on missing titles. *Fix*: Use `p.get("title", "No Title")` consistently.

- **Code Duplication**: `get_users`, `get_posts`, and `get_todos` share identical logic (fetch → cache → return). *Recommendation*: Replace with a single `fetch_and_cache` helper or use a parameterized endpoint.

- **Overly Broad Exception Handling**: `fetch()` catches all exceptions and returns error strings. This masks issues like network failures. *Fix*: Handle specific exceptions (e.g., `requests.exceptions.RequestException`) and avoid silent failure.

- **Inconsistent Error Format**: Error responses (`{"error": "..."}`) differ structurally from success data (list/dict). *Recommendation*: Standardize return types (e.g., use `None` for errors or raise exceptions).

- **Missing Documentation**: No docstrings for `APIClient`, `get_*` functions, or `process_all`. *Fix*: Add brief descriptions of purpose and return values.

- **Hardcoded Endpoints**: Endpoints (`/users`, `/posts`, etc.) are duplicated in multiple functions. *Recommendation*: Define endpoints in a constants module or as class attributes.

- **Redundant Cache Writes**: Cache is written even when `fetch()` returns an error. *Fix*: Only cache successful responses.

*Note*: The cache design and error handling require the most urgent attention to prevent runtime crashes and improve maintainability. The bug in the posts loop is particularly critical as it will fail immediately in production.