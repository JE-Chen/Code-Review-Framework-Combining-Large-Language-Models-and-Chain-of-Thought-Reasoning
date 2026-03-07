### Code Smell Type: Duplicate Code
- **Problem Location:** The `get_users()`, `get_posts()`, and `get_comments()` functions all follow identical patterns for making HTTP GET requests.
- **Detailed Explanation:** These three functions implement nearly identical logic: they make a request to a given endpoint using `requests.get`, handle exceptions by printing errors and returning an empty list, and return JSON data. This duplication increases maintenance burden—any change to error handling or request structure requires updates in multiple places.
- **Improvement Suggestions:** Refactor into a single generic helper function that accepts an endpoint path and returns parsed JSON, reducing redundancy while keeping behavior consistent.
- **Priority Level:** High

---

### Code Smell Type: Global State Usage
- **Problem Location:** The use of `GLOBAL_RESULTS = []` at module level.
- **Detailed Explanation:** Using a global variable for storing intermediate or final results makes the code harder to test, debug, and reuse. It introduces hidden dependencies and can lead to side effects when the module is imported or reused in different contexts.
- **Improvement Suggestions:** Replace `GLOBAL_RESULTS` with a local list passed between functions or returned from `process_data`. Alternatively, encapsulate the state within a class if more complex behavior is needed.
- **Priority Level:** High

---

### Code Smell Type: Magic Numbers / Strings
- **Problem Location:** Hardcoded values like `"Special User"`, `"Long Post Title"`, `"Comment by email"` and thresholds such as `20`, `10`, `50`.
- **Detailed Explanation:** These hardcoded strings and numeric values reduce readability and flexibility. If these need to be changed later, developers must manually locate each instance, increasing risk of oversight.
- **Improvement Suggestions:** Extract magic strings into constants (e.g., `SPECIAL_USER_MSG = "Special User:"`) and numeric thresholds into named variables or configuration settings.
- **Priority Level:** Medium

---

### Code Smell Type: Poor Error Handling
- **Problem Location:** In `get_users()`, `get_posts()`, and `get_comments()`, generic exception catching (`except Exception`) is used.
- **Detailed Explanation:** Catching all exceptions hides specific issues like connection timeouts, invalid responses, or malformed JSON. This prevents proper debugging and robustness in production environments.
- **Improvement Suggestions:** Catch specific exceptions like `requests.exceptions.RequestException` and handle them appropriately. Log errors instead of printing them for better observability.
- **Priority Level:** Medium

---

### Code Smell Type: Violation of Single Responsibility Principle
- **Problem Location:** The `process_data()` function handles fetching data, filtering, and logging results.
- **Detailed Explanation:** This function performs multiple responsibilities — data retrieval, business logic, and output formatting — violating SRP. As complexity grows, this makes testing and modification difficult.
- **Improvement Suggestions:** Split `process_data()` into smaller functions: one for fetching data, another for applying filters, and a third for displaying or storing results.
- **Priority Level:** High

---

### Code Smell Type: Inconsistent Conditional Logic
- **Problem Location:** Nested `if` statements in the `main()` function for determining result count categories.
- **Detailed Explanation:** The nested conditional blocks are hard to read and maintain. They could be simplified using elif chains or mapping thresholds to messages for cleaner control flow.
- **Improvement Suggestions:** Replace nested conditionals with a simple loop or dictionary-based lookup for categorizing result counts, improving readability and extensibility.
- **Priority Level:** Medium

---

### Code Smell Type: Lack of Input Validation and Security Considerations
- **Problem Location:** No validation on input parameters (none expected), nor any sanitization of external API responses.
- **Detailed Explanation:** Although the current code doesn't take user input directly, relying on untrusted external APIs without validating or sanitizing response data opens up potential vulnerabilities (e.g., injection attacks, unexpected formats). Also, lack of rate limiting or retries might cause instability under high load.
- **Improvement Suggestions:** Add checks for expected fields in API responses, sanitize outputs before logging, and consider implementing retry mechanisms or timeouts for HTTP calls.
- **Priority Level:** Medium

---

### Code Smell Type: Missing Documentation and Comments
- **Problem Location:** Minimal or no inline comments or docstrings provided.
- **Detailed Explanation:** Without documentation, other developers struggle to understand the purpose of functions, especially those performing complex filtering logic or managing global state. This hampers collaboration and future modifications.
- **Improvement Suggestions:** Add docstrings to explain what each function does, including parameters and return types. Include inline comments where necessary to clarify non-obvious operations.
- **Priority Level:** Low

---

### Code Smell Type: Tight Coupling Between Functions
- **Problem Location:** `main()` depends heavily on `process_data()` which uses `GLOBAL_RESULTS`.
- **Detailed Explanation:** The tight coupling between components reduces modularity and makes it harder to swap implementations or isolate units during testing.
- **Improvement Suggestions:** Pass data explicitly through parameters rather than relying on global variables. This allows easier unit testing and decouples modules.
- **Priority Level:** Medium

---