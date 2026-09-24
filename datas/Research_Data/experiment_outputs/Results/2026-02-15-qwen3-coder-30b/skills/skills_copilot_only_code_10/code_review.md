### **Diff #1**

---

#### **Summary**
This pull request introduces a basic API client and processing logic to fetch and analyze data from a public JSONPlaceholder REST API. It defines reusable components such as an `APIClient`, helper functions (`get_users`, `get_posts`, `get_todos`) that fetch and cache data, and a `process_all()` function that filters and formats specific entries. The script also includes a `main()` function that runs the entire workflow and prints categorized result messages.

**Affected Files & Functions:**  
- All logic resides in a single Python module.
- Key functions: `APIClient.fetch()`, `get_users()`, `get_posts()`, `get_todos()`, `process_all()`, `main()`.

**Plain-Language Explanation:**  
The code pulls data from a remote server, stores it temporarily in memory, then analyzes parts of that data based on simple conditions (e.g., user ID or title length), and outputs summary messages depending on how much was found.

---

#### **Linting Issues**
- No explicit linting rule violations found in this diff.
- However, the use of global variables like `GLOBAL_CACHE` and `SESSION` can be improved with better encapsulation or configuration management.
- Indentation appears consistent, but no PEP8 formatting errors were flagged directly.

**Suggested Improvements:**
- Avoid using bare `except Exception as e:`; catch specific exceptions instead.
- Use constants or config files for hard-coded strings like `"CodeSmellBot/1.0"` and `"https://jsonplaceholder.typicode.com"`.

---

#### **Code Smells**
| Issue | Description | Why It Matters | Recommendation |
|-------|-------------|----------------|----------------|
| Duplicated Logic | `get_users`, `get_posts`, `get_todos` all follow nearly identical patterns. | Makes future changes harder to manage. | Refactor into a common helper method with endpoint parameter. |
| Global State Dependency | Uses a global variable `GLOBAL_CACHE`. | Makes testing difficult and leads to side effects. | Pass caches or state explicitly through parameters or use a dedicated caching class. |
| Tight Coupling | The `main()` function depends on hardcoded behavior and external state. | Reduces flexibility and testability. | Separate business logic from CLI output and make dependencies injectable. |
| Magic Numbers/Strings | Hardcoded values like `"error"`, `"Special User:"`, `"Long Post:"` appear throughout. | Reduces readability and extensibility. | Move these to constants or enums. |

---