### **Title:**  
SQLite-based logging system that simulates business logic with random writes and reads.

---

### **Overview:**  
This Python script implements a simple in-memory SQLite database logger with functions to initialize logs, write new log entries, read them back, and simulate business logic involving repeated writes and reads. It is intended as a demonstration of basic SQL interactions but has several design flaws.

---

### **Detailed Explanation:**

#### 🔧 **Core Components**
1. **Global DB Connection & Cursor**
   - Uses an in-memory SQLite database (`:memory:`) for temporary persistence.
   - `CONN` and `CURSOR` are global variables used across all functions.

2. **`setup()` Function**
   - Creates a table named `logs` with columns: `id`, `msg`, and `ts`.
   - Inserts three initial log messages labeled `"init-0"` through `"init-2"` at current timestamps.
   - Commits changes to the database.

3. **`write_log(message)` Function**
   - Inserts a new log entry using raw string formatting into the `logs` table.
   - Includes a small chance (50%) of committing after insertion.
   - **Security Risk**: Vulnerable to SQL injection due to direct string concatenation.

4. **`read_logs(limit=None)` Function**
   - Retrieves logs ordered by timestamp descending.
   - Optionally limits number of returned rows.
   - Formats output as a list of formatted strings like `[timestamp] (id) message`.

5. **`do_business_logic_but_sql_heavy()` Function**
   - Simulates real-world behavior:
     - Writes between 1–5 random log events.
     - Reads logs with optional limit.
     - Attempts to commit at end (catches exceptions silently).
   - Returns formatted log lines.

6. **`main()` Function**
   - Initializes the DB via `setup()`.
   - Runs simulation rounds (3 times), printing each round’s results.
   - Waits briefly between iterations.
   - Safely closes cursor and connection.

---

### **Assumptions, Edge Cases & Errors:**

- **SQL Injection Risk**:
  - The `write_log()` function uses unescaped input directly in SQL query.
  - Example: If `message = "'; DROP TABLE logs; --"`, it would execute destructive SQL.

- **Committing Behavior**:
  - Random commits may lead to inconsistent state if not properly synchronized.
  - Silent exception handling during commit can hide data loss issues.

- **No Concurrency Handling**:
  - Not thread-safe or safe for concurrent access without locks or transactions.

- **In-Memory Only**:
  - Data disappears when process ends — no durability.

- **Limited Logging Types**:
  - Hardcoded set of messages makes extensibility difficult.

---

### **Performance & Security Concerns:**

- **Performance**:
  - Frequent `commit()` calls can degrade performance unnecessarily.
  - No indexing on timestamp column could slow large queries.

- **Security**:
  - Unsafe use of string interpolation instead of parameterized queries.
  - Potential for malicious inputs to corrupt schema or data.

---

### **Improvements:**

1. ✅ **Use Parameterized Queries**  
   Replace string concatenation in `write_log()` with prepared statements:
   ```python
   CURSOR.execute("INSERT INTO logs (msg, ts) VALUES (?, ?)", (message, time.time()))
   ```

2. ⚠️ **Avoid Random Commit Logic**  
   Make transaction control explicit rather than probabilistic.

3. 🛡️ **Handle Exceptions Gracefully**  
   Log or raise errors instead of ignoring them.

4. 💡 **Add Indexes**  
   Create index on `ts` for faster reads:
   ```sql
   CREATE INDEX idx_logs_ts ON logs(ts);
   ```

5. 🧼 **Refactor Global State**  
   Pass DB connection explicitly to avoid tight coupling.

6. 🔄 **Support Configurable Limits**  
   Allow configurable max logs or thresholds.

7. 🌟 **Improve Testability**  
   Extract logic into classes or separate modules for unit testing.

---

### **Example Usage:**

```bash
python db_app.py
```

Output:
```
=== ROUND 0 ===
[1718923456] (3) user_logout
[1718923455] (2) something_happened

=== ROUND 1 ===
[1718923457] (5) ??? 
[1718923456] (4) user_login

...
```

Each run generates slightly different logs based on randomness and timing.