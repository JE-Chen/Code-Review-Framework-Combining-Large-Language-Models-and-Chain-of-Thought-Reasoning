### Diff #1: New file `db_app.py`

---

### **Summary**  
This code introduces a new in-memory SQLite logging system for simulation purposes. The file defines database setup, log writing/reading utilities, and a business logic simulation that generates random log entries. Key components include:  
- **Database setup** (`setup`): Creates a `logs` table and populates it with 3 initial entries.  
- **Log operations** (`write_log`, `read_logs`): Inserts messages with timestamps and retrieves logs with optional limits.  
- **Simulation logic** (`do_business_logic_but_sql_heavy`): Writes random logs, reads them, and prints results.  
- **Main entry point** (`main`): Runs the simulation 3 times with sleep intervals.  
*Plain-language explanation*: This is a test utility that mimics a logging service using SQLite, simulating user activity and printing logs. It’s designed for demonstration, not production use.

---

### **Linting Issues**  
- **SQL Injection Risk** (Line 21):  
  `f"INSERT INTO logs (msg, ts) VALUES ('{message}', {time.time()})"`  
  → *Violates security best practices*. User-provided `message` is directly interpolated into SQL.  
  → *Fix*: Use parameterized queries:  
  ```python
  CURSOR.execute("INSERT INTO logs (msg, ts) VALUES (?, ?)", (message, time.time()))
  ```

- **Excessive Blank Lines** (Lines 3–4, 12–13, 21–22, etc.):  
  → *Violates style guides* (e.g., PEP 8). Blank lines should separate logical blocks, not functions.  
  → *Fix*: Reduce to 1 blank line between functions.

- **Magic Numbers** (Lines 10, 26, 37, 41):  
  `range(3)`, `random.randint(1, 5)`, `random.choice([None, 2, 5])`  
  → *Hardcoded values lack context*.  
  → *Fix*: Define constants (e.g., `INITIAL_LOGS = 3`).

---

### **Code Smells**  
- **Global Database State** (Lines 3–4, used everywhere):  
  → *Problem*: Coupled to global `CONN`/`CURSOR`, making code non-testable and prone to side effects.  
  → *Fix*: Encapsulate in a `Database` class with dependency injection.

- **Non-Deterministic Commits** (Line 25):  
  `if random.choice([True, False]): CONN.commit()`  
  → *Problem*: Random commits risk data loss on crash. Commit logic must be deterministic.  
  → *Fix*: Move commit to caller (e.g., `do_business_logic_but_sql_heavy` should handle it).

- **Poor Error Handling** (Line 43):  
  `try: CONN.commit() except Exception: pass`  
  → *Problem*: Silently ignores commit failures.  
  → *Fix*: Log errors or propagate exceptions.

- **Confusing Log Format** (Line 35):  
  `f"[{int(ts)}] ({i}) {msg}"`  
  → *Problem*: Truncates timestamps (`int(ts)`) and uses ambiguous IDs.  
  → *Fix*: Use ISO timestamps and structured output (e.g., JSON).

- **Overly Complex Simulation** (Line 37):  
  `do_business_logic_but_sql_heavy` mixes log writing, reading, and business logic.  
  → *Problem*: Violates Single Responsibility Principle.  
  → *Fix*: Split into `generate_logs()`, `fetch_logs()`, and `print_results()`.

- **Hardcoded Simulation Parameters** (Lines 10, 37, 41):  
  → *Problem*: Values like `3` (initial logs) and `2`/`5` (limits) are scattered.  
  → *Fix*: Centralize in a config object or constants.