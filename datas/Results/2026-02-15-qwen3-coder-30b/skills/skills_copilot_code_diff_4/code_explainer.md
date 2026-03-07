### **Title:**  
SQLite database interaction with hardcoded user data and basic CRUD operations.

---

### **Overview:**  
This script connects to a SQLite database (`test.db`), creates a table called `users`, inserts two sample records ("Alice" and "Bob"), retrieves them, and prints matching results. It demonstrates basic SQL operations using Python's built-in `sqlite3` module.

---

### **Detailed Explanation:**

#### **Flow & Components:**
- **Global Variables:**
  - `conn`: Connection object to the SQLite database.
  - `cursorThing`: Cursor used for executing SQL commands.

- **Main Function (`functionThatDoesTooManyThingsAndIsHardToRead`):**
  1. Initializes connection and cursor to `test.db`.
  2. Attempts to create a table named `users` if not already present.
     - If creation fails, it silently ignores the error.
  3. Inserts two rows into the `users` table:
     - First row: `"Alice", 25`
     - Second row: `"Bob", 30`
     - Uses string concatenation for SQL queries — **vulnerable to injection**.
  4. Executes a SELECT query to fetch all rows from the `users` table.
     - Loops through fetched rows and prints info based on name match:
       - Specific handling for "Alice" and "Bob".
       - Default case for others.
  5. Commits changes and closes the database connection.

- **Entry Point:**
  - Runs the main function when executed directly.

---

### **Assumptions, Edge Cases & Errors:**

- **No Input Validation:**
  - Hardcoded values make this inflexible.
  - No checks for duplicate names or invalid types.

- **SQL Injection Risk:**
  - Concatenated strings in SQL queries expose the app to malicious input.

- **Error Handling:**
  - Catches exceptions but discards details.
  - Silently ignores failures during table creation and selection.

- **Database State:**
  - Does not account for existing data or concurrent access.

---

### **Performance & Security Concerns:**

- **Security Issues:**
  - Use of raw string concatenation makes the code vulnerable to SQL injection attacks.

- **Performance:**
  - No use of parameterized queries.
  - Repeated manual commits and closing may be inefficient.

- **Scalability:**
  - Global state management increases complexity and reduces testability.

---

### **Improvements:**

1. **Use Parameterized Queries:**
   - Replace string concatenation with placeholders (`?`) for safe execution.

2. **Avoid Global Variables:**
   - Encapsulate logic inside classes or functions with proper scope.

3. **Improve Error Handling:**
   - Log meaningful exceptions instead of ignoring them.

4. **Modularize Logic:**
   - Split functionality into smaller reusable functions (e.g., setup, insert, query).

5. **Add Input Validation:**
   - Validate inputs before insertion.

6. **Handle Concurrency:**
   - Consider locking mechanisms or transactions where needed.

7. **Testing Support:**
   - Refactor into testable units.

---

### **Example Usage:**

```bash
python sql_app.py
```

Expected Output:
```
找到 Alice: (1, 'Alice', 25)
找到 Bob: (2, 'Bob', 30)
```

> Note: This assumes no prior data exists and the DB is writable. In production, you'd want better control over such behavior.