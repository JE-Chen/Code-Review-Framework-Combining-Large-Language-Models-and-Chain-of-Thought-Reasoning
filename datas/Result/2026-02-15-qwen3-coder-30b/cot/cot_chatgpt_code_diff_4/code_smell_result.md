---

### Code Smell Type: Global State Dependency
- **Problem Location:** `CONN` and `CURSOR` defined at module level.
- **Detailed Explanation:** The use of global variables (`CONN`, `CURSOR`) makes the code tightly coupled to a fixed database instance. This hinders modularity, testability, and reuse. It also introduces hidden dependencies that can lead to race conditions or unexpected behavior when running multiple instances or in concurrent environments.
- **Improvement Suggestions:** Encapsulate database access within classes or functions that accept connections as parameters. Use dependency injection where applicable.
- **Priority Level:** High

---

### Code Smell Type: SQL Injection Vulnerability
- **Problem Location:** In `write_log()` function — string interpolation into SQL query without sanitization.
- **Detailed Explanation:** Using f-strings to build SQL queries exposes the application to SQL injection attacks. Even if this is a demo, such patterns are dangerous and should never be used in production.
- **Improvement Suggestions:** Replace direct string concatenation with parameterized queries using placeholders like `?` in SQLite.
- **Priority Level:** High

---

### Code Smell Type: Magic Numbers and Strings
- **Problem Location:** 
  - `"init-{i}"` in `setup()`  
  - Random choices in `do_business_logic_but_sql_heavy()`  
  - Hardcoded limits and intervals in `read_logs()` and `main()`
- **Detailed Explanation:** These values lack semantic meaning and make code harder to understand and change. They reduce flexibility and increase risk of inconsistencies.
- **Improvement Suggestions:** Extract constants or configuration options for these values. Define enums or named constants for repeated strings and numbers.
- **Priority Level:** Medium

---

### Code Smell Type: Poor Error Handling
- **Problem Location:** Empty `except Exception:` block in `do_business_logic_but_sql_heavy()`.
- **Detailed Explanation:** Catching exceptions and silently ignoring them hides real issues, making debugging difficult. It could mask failures in transaction commits or other critical operations.
- **Improvement Suggestions:** Log errors appropriately or re-raise them after inspection. At minimum, log what went wrong instead of doing nothing.
- **Priority Level:** High

---

### Code Smell Type: Lack of Input Validation
- **Problem Location:** `write_log()` accepts any message string without validation.
- **Detailed Explanation:** No checks on input size, format, or content may result in malformed data or performance degradation due to oversized messages.
- **Improvement Suggestions:** Add validation for message length and type. Sanitize inputs before insertion.
- **Priority Level:** Medium

---

### Code Smell Type: Tight Coupling Between Business Logic and DB Access
- **Problem Location:** `do_business_logic_but_sql_heavy()` mixes business logic with raw DB calls.
- **Detailed Explanation:** Mixing concerns reduces testability and increases complexity. This violates the separation of concerns principle.
- **Improvement Suggestions:** Separate domain logic from persistence logic. Abstract away DB interactions behind service layers.
- **Priority Level:** High

---

### Code Smell Type: Unnecessary Complexity in Formatting
- **Problem Location:** List comprehension in `read_logs()` returns formatted strings.
- **Detailed Explanation:** Formatting logic embedded inside data retrieval obscures responsibilities. It’s better to keep formatting separate for clarity and reuse.
- **Improvement Suggestions:** Return raw data from `read_logs()` and format it externally. Consider creating a dedicated formatter utility.
- **Priority Level:** Medium

---

### Code Smell Type: Inconsistent Use of Commit Behavior
- **Problem Location:** `write_log()` conditionally commits based on random choice.
- **Detailed Explanation:** This unpredictable behavior makes transactions unreliable and hard to reason about. It can lead to partial writes or inconsistent state.
- **Improvement Suggestions:** Make commit strategy explicit and deterministic. Either always commit or never commit unless explicitly requested.
- **Priority Level:** High

---

### Code Smell Type: Lack of Modularity and Testability
- **Problem Location:** All functions are top-level, no clear structure or encapsulation.
- **Detailed Explanation:** Without classes or modules, testing becomes challenging. Unit tests cannot isolate components effectively.
- **Improvement Suggestions:** Refactor into a class-based architecture where each responsibility is encapsulated. Provide mockable interfaces for testing.
- **Priority Level:** Medium

---

### Code Smell Type: Redundant Operations
- **Problem Location:** `try/except` block around `CONN.commit()` in `do_business_logic_but_sql_heavy()`.
- **Detailed Explanation:** If `commit()` fails due to an already-committed transaction, catching it silently is likely incorrect usage rather than a valid error case.
- **Improvement Suggestions:** Remove redundant try-except or handle the correct failure modes properly.
- **Priority Level:** Medium

---

### Code Smell Type: Hardcoded Time Delays
- **Problem Location:** `time.sleep(0.2)` in `main()`.
- **Detailed Explanation:** Hardcoded delays make timing assumptions brittle and reduce portability. Could interfere with automated testing or real-world performance expectations.
- **Improvement Suggestions:** Allow delay to be configurable or removed entirely in favor of event-driven execution or proper async support.
- **Priority Level:** Low

---

### Summary Table:

| Code Smell Type                         | Priority |
|----------------------------------------|----------|
| Global State Dependency                | High     |
| SQL Injection Vulnerability            | High     |
| Magic Numbers and Strings              | Medium   |
| Poor Error Handling                    | High     |
| Lack of Input Validation               | Medium   |
| Tight Coupling Between Logic & DB      | High     |
| Inconsistent Use of Commit Behavior    | High     |
| Lack of Modularity and Testability     | Medium   |
| Redundant Operations                   | Medium   |
| Hardcoded Time Delays                  | Low      |

--- 

This review identifies key areas needing improvement while respecting the intent of the original code. Prioritizing high-severity issues will significantly improve reliability, maintainability, and scalability.