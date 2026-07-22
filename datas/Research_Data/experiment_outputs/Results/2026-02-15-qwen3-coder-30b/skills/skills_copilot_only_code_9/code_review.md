### **Diff #1**

---

#### **1. Summary**
This PR introduces a Python script that fetches data from the JSONPlaceholder REST API for users, posts, and comments. It processes this data to identify special cases like a specific user (ID=5), long post titles, and comments associated with emails containing "@". The filtered results are stored globally and printed out along with a summary message based on result count.

**Affected components:**  
- Functions: `get_users`, `get_posts`, `get_comments`, `process_data`, `main`  
- Global variable: `GLOBAL_RESULTS`  
- External dependency: `requests`

**Plain-language explanation:**  
The script pulls in sample data from an online service, checks certain conditions on it, stores matching entries in a list, and then prints those matches along with how many there were.

---

#### **2. Linting Issues**
- **No explicit PEP8 violations found**, but could benefit from minor stylistic improvements.
- **Missing docstrings** for all functions (`get_users`, `get_posts`, etc.) — recommended for clarity.
- **Magic string usage**: `"https://jsonplaceholder.typicode.com"` should be extracted into a constant if reused elsewhere.
- **Inconsistent exception handling messages**: All error messages use generic prefixes ("Error in ..."), which can be improved for better logging consistency.

**Suggested corrections:**
- Add function-level docstrings.
- Define base URL as a named constant.
- Improve logging format consistency across exceptions.

---

#### **3. Code Smells**
- **Global state abuse**: Using `GLOBAL_RESULTS` makes the function non-deterministic and hard to test or reuse.
- **Duplicated logic**: Each getter (`get_users`, `get_posts`, `get_comments`) has nearly identical structure and error handling.
- **Tight coupling to external APIs**: Direct reliance on hardcoded endpoints without abstraction or configuration options.
- **Poor control flow nesting**: Nested conditional blocks in `main()` make reading harder than necessary.
- **Lack of modularity**: Filtering logic exists directly inside `process_data()` instead of being broken into reusable helper functions.

**Improvement suggestions:**
- Replace global variables with return values or proper state management.
- Extract common HTTP request logic into a utility function.
- Modularize filtering logic using separate functions per rule.
- Refactor conditionals to reduce nesting levels.
- Introduce configuration or mocking layers for easier testing.

---