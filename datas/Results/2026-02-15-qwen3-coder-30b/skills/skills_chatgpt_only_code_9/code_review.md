### **Diff #1**

---

### **1. Summary**

- **Purpose**: This PR introduces a basic API client using `requests`, fetches user, post, and todo data from a placeholder REST API (`jsonplaceholder.typicode.com`), caches it globally, and processes specific conditions on fetched data.
- **Affected Components**:
  - `APIClient`: A class that wraps HTTP requests.
  - `get_users`, `get_posts`, `get_todos`: Helper functions to fetch resources.
  - `process_all()`: Main logic for filtering and collecting results.
  - `main()`: Entry point printing results and categorizing them by count.
- **Plain-Language Explanation**: The script fetches sample data from an online service, applies simple filters to find certain items (e.g., long titles or incomplete tasks), and prints summary messages based on how many matches were found.

---

### **2. Linting Issues**

- ❌ **Missing docstrings** for classes and functions.
  - *Example*: No documentation for `APIClient`, `get_users`, or `process_all`.
- ❌ **Use of global variables** like `GLOBAL_CACHE` and `SESSION`.
  - *Issue*: Makes testing harder and introduces side effects.
- ❌ **Inconsistent naming** — e.g., function names don’t follow snake_case consistently.
- ❌ **Magic strings** used directly in conditionals (`"users"`, `"posts"`, `"todos"`).
- ✅ **Suggestion**: Use constants for string keys and add type hints where appropriate.

---

### **3. Code Smells**

- 🧼 **Duplication**: Similar logic exists in `get_users`, `get_posts`, and `get_todos`.
  - *Problem*: Hard to maintain; if logic changes, all must be updated manually.
  - *Fix*: Refactor into a generic method with parameters.
- ⚠️ **Global State Usage**:
  - *Problem*: Relies on mutable global state (`GLOBAL_CACHE`) which can lead to race conditions or unexpected behavior.
  - *Fix*: Pass cache as dependency or make it thread-safe.
- 🔁 **Tight Coupling**:
  - *Problem*: Functions depend heavily on shared state and hardcoded endpoints.
  - *Fix*: Introduce configuration or dependency injection.
- 📦 **Poor Separation of Concerns**:
  - *Problem*: Business logic (filtering & processing) is mixed with I/O and display logic.
  - *Fix*: Separate concerns into smaller, testable units.

---