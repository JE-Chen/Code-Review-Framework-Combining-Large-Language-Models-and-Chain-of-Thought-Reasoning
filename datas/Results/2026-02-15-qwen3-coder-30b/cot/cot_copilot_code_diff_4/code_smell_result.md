### Code Smell Type: Global State Usage
- **Problem Location:** `global conn, cursorThing` inside `functionThatDoesTooManyThingsAndIsHardToRead()`
- **Detailed Explanation:** The use of global variables (`conn`, `cursorThing`) makes the function stateful and tightly coupled to the environment. This reduces reusability, makes testing difficult, and introduces side effects that can lead to unpredictable behavior in concurrent environments.
- **Improvement Suggestions:** Replace global variables with local parameters or return values. Encapsulate database operations within a class or module where connection management is handled explicitly.
- **Priority Level:** High

---

### Code Smell Type: Magic Strings
- **Problem Location:** `"CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT, age INTEGER)"`, `"INSERT INTO users(name, age) VALUES(...)"`, `"SELECT * FROM users"`
- **Detailed Explanation:** Hardcoded SQL strings make code brittle and hard to maintain. If schema changes occur, these literals must be updated manually, increasing risk of errors.
- **Improvement Suggestions:** Define SQL queries as constants or methods to centralize them. Consider using an ORM or query builder library for safer query construction.
- **Priority Level:** High

---

### Code Smell Type: SQL Injection Vulnerability
- **Problem Location:** String concatenation in insert statements like `"' + name + "', " + str(age)`
- **Detailed Explanation:** Concatenating user input directly into SQL queries leaves room for malicious injection attacks. Even if inputs are controlled here, it's a dangerous pattern.
- **Improvement Suggestions:** Use parameterized queries instead of string concatenation. For example, `cursorThing.execute("INSERT INTO users(name, age) VALUES(?, ?)", (name, age))`.
- **Priority Level:** High

---

### Code Smell Type: Poor Exception Handling
- **Problem Location:** Catch-all `except Exception as e:` and bare `except:` clauses
- **Detailed Explanation:** Broad exception handling suppresses real issues and hinders debugging. It also masks legitimate failures without proper logging or recovery mechanisms.
- **Improvement Suggestions:** Catch specific exceptions where possible and log errors appropriately. Avoid ignoring exceptions silently unless there’s a valid reason.
- **Priority Level:** High

---

### Code Smell Type: Violation of Single Responsibility Principle
- **Problem Location:** `functionThatDoesTooManyThingsAndIsHardToRead()` performs multiple unrelated tasks: DB setup, data insertion, querying, printing results
- **Detailed Explanation:** A single function doing too much prevents modularity and reuse. Each logical operation should be separated into its own function or method.
- **Improvement Suggestions:** Split functionality into smaller functions such as `setup_database`, `insert_user`, `query_users`, and `print_results`.
- **Priority Level:** High

---

### Code Smell Type: Inconsistent Naming Convention
- **Problem Location:** `cursorThing`, `functionThatDoesTooManyThingsAndIsHardToRead`
- **Detailed Explanation:** Names like `cursorThing` lack clarity and don’t follow common naming conventions (e.g., camelCase). Function names suggest poor design rather than clear intent.
- **Improvement Suggestions:** Rename variables and functions to clearly reflect their purpose. E.g., `db_cursor`, `initialize_and_populate_database`.
- **Priority Level:** Medium

---

### Code Smell Type: Lack of Input Validation
- **Problem Location:** No validation of inputs before insertion or execution
- **Detailed Explanation:** Without validating inputs, invalid or unexpected data could corrupt the database or cause runtime exceptions.
- **Improvement Suggestions:** Add checks for valid types and ranges when inserting data. Validate both structure and content where applicable.
- **Priority Level:** Medium

---

### Code Smell Type: Unnecessary Logic Nesting
- **Problem Location:** Nested conditional blocks in result printing logic
- **Detailed Explanation:** Deep nesting reduces readability and increases cognitive load. It’s harder to trace control flow and spot edge cases.
- **Improvement Suggestions:** Flatten nested conditions using guard clauses or early returns. Prefer simple, linear logic over deeply nested structures.
- **Priority Level:** Medium

---

### Code Smell Type: Missing Return Values or Outputs
- **Problem Location:** Function does not return meaningful data
- **Detailed Explanation:** Functions that only perform side effects (like printing) are less reusable and harder to test in isolation.
- **Improvement Suggestions:** Return results from query operations and let calling code handle display or further processing.
- **Priority Level:** Medium

---

### Code Smell Type: Hardcoded Database Name
- **Problem Location:** `"test.db"` in `sqlite3.connect("test.db")`
- **Detailed Explanation:** Hardcoding database names limits portability and configurability. Different environments may require different DBs.
- **Improvement Suggestions:** Accept database path as a parameter or read from config/environment variables.
- **Priority Level:** Medium

---

### Code Smell Type: Redundant Condition Checks
- **Problem Location:** `if len(r) > 0:` followed by index access
- **Detailed Explanation:** Checking list length before accessing indices is redundant because fetching rows ensures they exist. This adds noise and confusion.
- **Improvement Suggestions:** Remove unnecessary checks. Trust that fetched rows contain expected fields.
- **Priority Level:** Low

---