### Title: In-Memory SQLite Logging System with Flawed Transaction Handling

### Overview
A simple logging application using an in-memory SQLite database to record messages with timestamps. It demonstrates basic database operations but contains critical security flaws and inconsistent transaction management. The business logic writes random logs and reads them with optional limits.

---

### Detailed Explanation
#### Core Components & Flow
1. **Global Database Setup** (`CONN`, `CURSOR`):
   - Uses SQLite's `:memory:` database (in-memory, no disk persistence).
   - Connection and cursor initialized at module scope.

2. **`setup()`**:
   - Creates `logs` table with `id` (PK), `msg` (TEXT), `ts` (REAL timestamp).
   - Inserts 3 initial logs (`init-0`, `init-1`, `init-2`).

3. **`write_log(message)`**:
   - **Input**: Untrusted string `message`.
   - **Flow**:
     1. Constructs SQL via string interpolation:  
        `INSERT INTO logs (msg, ts) VALUES ('{message}', {time.time()})`.
     2. Executes INSERT.
     3. Randomly commits (50% chance) via `CONN.commit()`.
   - **Critical Flaw**: SQL injection vulnerability (see *Security* below).

4. **`read_logs(limit=None)`**:
   - **Input**: Optional integer `limit` (e.g., `2`).
   - **Flow**:
     1. Builds query: `SELECT id, msg, ts FROM logs ORDER BY ts DESC`.
     2. Appends `LIMIT {limit}` if provided.
     3. Fetches rows and formats as `[timestamp] (id) message`.
   - **Edge Case**: `ts` truncated to integer (e.g., `1717000000.123` → `1717000000`).

5. **`do_business_logic_but_sql_heavy()`**:
   - **Flow**:
     1. Writes 1–5 random logs (e.g., `user_login`).
     2. Reads logs with random limit (`None`, `2`, or `5`).
     3. Tries to commit (ignores exceptions).
   - **Flaw**: Redundant commit (writes may already be committed).

6. **`main()`**:
   - Runs business logic 3 times.
   - Prints formatted logs after each round.
   - Closes connection after execution.

---

### Key Assumptions & Edge Cases
| Component               | Assumption                          | Edge Case/Problem                                                                 |
|-------------------------|-------------------------------------|---------------------------------------------------------------------------------|
| `write_log()`           | `message` is safe                   | **SQL injection**: `' OR 1=1 --` breaks query (e.g., drops table).                |
| `read_logs()`           | `ts` is always valid REAL           | Truncated timestamps lose precision (e.g., `1717000000.999` → `1717000000`).       |
| Random commit in `write_log` | Commit probability 50%          | **Data loss risk**: Uncommitted writes lost on crash.                            |
| `do_business_logic_but_sql_heavy()` | Writes are atomic          | Reads may see stale data if commit didn't occur (non-deterministic).              |
| `limit` in `read_logs`  | `limit` is integer or `None`        | `limit` passed as string (e.g., `"5"`) causes SQL error.                         |

---

### Security & Performance Concerns
| Issue                          | Severity | Impact                                                                 |
|--------------------------------|----------|------------------------------------------------------------------------|
| **SQL Injection**              | Critical | Malicious `message` could delete database, exfiltrate data, or corrupt logs. |
| **Non-deterministic Commits**  | High     | Uncommitted writes lost on crash; inconsistent state.                   |
| **Redundant Commit**           | Medium   | `do_business_logic_but_sql_heavy` commits twice (unnecessary I/O).        |
| **Truncated Timestamps**       | Low      | Logs lose millisecond precision (unimportant for basic logging).         |

---

### Improvements
1. **Fix SQL Injection**  
   Replace string interpolation with parameterized queries:
   ```python
   # BEFORE (vulnerable)
   sql = f"INSERT INTO logs (msg, ts) VALUES ('{message}', {time.time()})"
   
   # AFTER (secure)
   CURSOR.execute("INSERT INTO logs (msg, ts) VALUES (?, ?)", (message, time.time()))
   ```

2. **Remove Random Commits**  
   Control transactions explicitly in business logic:
   ```python
   # In do_business_logic_but_sql_heavy():
   for _ in range(random.randint(1, 5)):
       write_log(...)  # No commit here
   # Commit once after all writes
   CONN.commit()
   ```

3. **Improve Timestamp Handling**  
   Use `datetime` for readable timestamps (optional):
   ```python
   # In read_logs()
   return [f"[{datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')}] ({i}) {msg}" for ...]
   ```

4. **Validate `limit` Input**  
   Ensure `limit` is integer or `None`:
   ```python
   if limit is not None and not isinstance(limit, int):
       raise ValueError("limit must be integer or None")
   ```

5. **Remove Redundant Commit**  
   Delete the `try` block in `do_business_logic_but_sql_heavy()` (commit is now handled in business logic).

---

### Example Usage
**Run the script**:
```bash
python db_app.py
```
**Output** (simplified):
```
=== ROUND 0 ===
[1717000000] (3) init-2
[1717000000] (2) init-1
[1717000000] (1) init-0
[1717000000] (4) user_login
=== ROUND 1 ===
[1717000000] (5) ??? 
[1717000000] (4) user_login
...
```

---

### Why This Matters
- **Security**: The SQL injection vulnerability makes this code unsafe for production. Parameterized queries are non-negotiable.
- **Reliability**: Random commits create hidden failure modes (data loss). Explicit transactions prevent this.
- **Maintainability**: Clear commit boundaries and input validation make code predictable and debuggable.
- **Best Practice**: Always treat user input as untrusted. Use parameters for SQL queries. Control transactions at the business logic layer.