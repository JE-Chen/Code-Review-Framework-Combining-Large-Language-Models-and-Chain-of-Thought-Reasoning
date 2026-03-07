# Code Review: db_app.py

## Critical Security Risk
- **SQL Injection Vulnerability**: `write_log` uses string interpolation for SQL queries (`f"INSERT ... VALUES ('{message}', ..."`), enabling malicious input to manipulate queries.  
  **Fix**: Always use parameterized queries (e.g., `CURSOR.execute("INSERT ...", (message, time.time()))`).

## Major Design Issues
- **Non-Deterministic Commits**: `write_log` randomly commits (via `random.choice`), risking data loss/inconsistency if the program crashes mid-transaction.  
  **Fix**: Commit only when the transaction is complete (e.g., after all operations in `do_business_logic_but_sql_heavy`).
- **Global State**: Hardcoded `CONN`/`CURSOR` globals prevent testability and reuse.  
  **Fix**: Inject database dependencies (e.g., via constructor or context managers).
- **Business Logic Coupling**: `do_business_logic_but_sql_heavy` mixes database operations with business logic.  
  **Fix**: Separate database access (e.g., repository pattern) from business logic.

## Code Quality & Clarity
- **Ambiguous Naming**: `do_business_logic_but_sql_heavy` is unprofessional and unclear.  
  **Fix**: Rename to `process_user_activity` or similar.
- **Timestamp Handling**: `int(ts)` truncates precision (e.g., `1717000000.123` → `1717000000`).  
  **Fix**: Format as string (e.g., `f"{ts:.3f}"`) or keep as float.
- **Redundant Commit**: `do_business_logic_but_sql_heavy` attempts a commit after `write_log` (which may already have committed).  
  **Fix**: Remove redundant commit.
- **Missing Documentation**: No docstrings for public functions.  
  **Fix**: Add concise descriptions (e.g., "Write log entry with timestamp").

## Minor Issues
- **Excessive Blank Lines**: Inconsistent spacing (e.g., 3 blank lines between `CURSOR` and `setup`).  
  **Fix**: Standardize to 1 blank line between functions.
- **Unnecessary `try`/`except`**: Swallows commit exceptions without logging.  
  **Fix**: Either handle or remove (e.g., only commit when needed).

## Testing & Maintainability
- **No Tests**: Critical path (SQL operations) lacks unit tests.  
  **Fix**: Add tests for `write_log`, `read_logs`, and transaction handling.
- **Hardcoded DB**: `:memory:` is fine for demos but unsuitable for production.  
  **Fix**: Parameterize DB connection (e.g., via config).

---

## Recommendations Summary
| Category          | Issue                                                                 | Priority |
|-------------------|-----------------------------------------------------------------------|----------|
| **Security**      | SQL injection in `write_log` (critical)                               | Blocker  |
| **Design**        | Random commits + global state (major)                                 | High     |
| **Clarity**       | Unclear function name + timestamp truncation (minor)                  | Medium   |
| **Maintainability**| Missing docstrings + tests (critical for production)                   | High     |

**Action Required**: Address security vulnerability first, then refactor for testability. Avoid global state and random commits.