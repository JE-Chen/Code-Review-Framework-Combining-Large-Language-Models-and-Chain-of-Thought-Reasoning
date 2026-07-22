### Summary
This PR introduces a Python script that utilizes a custom API client (`APIClient`) to fetch data from a JSON placeholder API and processes it. The script caches fetched data globally and categorizes certain items based on specific conditions.

**Affected Files:**  
- `script.py`

**Plain-Language Explanation:**  
The script connects to an external API to retrieve user, post, and todo data. It then filters and prints out special cases based on predefined criteria.

---

### Linting Issues
- **PEP8 Compliance Violations:**
  - **Line Length Exceeded:** Lines exceed the recommended maximum length of 79 characters.
    - *File:* `script.py`
    - *Lines:* 16, 40, 52, 65, 78, 91
  - **Missing Docstrings:** Functions like `get_users`, `get_posts`, `get_todos`, and `process_all` lack docstrings.
    - *File:* `script.py`
    - *Functions:* `get_users`, `get_posts`, `get_todos`, `process_all`

- **Style Consistency:**
  - **Variable Naming:** Use snake_case instead of camelCase for variable names.
    - *File:* `script.py`
    - *Variables:* `SESSION`, `BASE_URL`, `GLOBAL_CACHE`

### Code Smells
- **Global State Usage:**
  - The use of a global cache dictionary (`GLOBAL_CACHE`) can lead to unexpected side effects and make testing difficult.
  - *Recommendation:* Refactor to pass necessary data between functions explicitly.

- **Large Functions:**
  - The `process_all` function is quite large and does multiple things. It should be broken down into smaller, more focused functions.
  - *Example:* Extract filtering logic into separate functions.

- **Magic Numbers:**
  - Magic numbers like `5` and `20` are used in conditional statements. These should be replaced with named constants for better readability.
  - *Example:* Define constants at the top of the module.

- **Redundant Error Handling:**
  - The error handling in `fetch` method could be simplified. Currently, it catches all exceptions without providing useful information.
  - *Recommendation:* Catch specific exceptions or rethrow them with additional context.

- **Hardcoded Strings:**
  - Hardcoded strings like `"User-Agent"` and `"CodeSmellBot/1.0"` are repeated. Consider using a configuration file or environment variables.
  - *Recommendation:* Create a configuration class or settings module.

---

By addressing these issues, the code will become more maintainable, readable, and adherent to standard Python coding conventions.