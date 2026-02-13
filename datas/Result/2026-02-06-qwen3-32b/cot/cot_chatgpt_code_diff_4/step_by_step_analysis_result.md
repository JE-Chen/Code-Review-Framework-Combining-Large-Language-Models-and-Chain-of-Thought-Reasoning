### Code Quality Review Report

---

#### **1. SQL Injection Vulnerability**  
**Issue**:  
Directly interpolating user input (`message`) into a SQL string without validation.  
**Why it matters**:  
This exposes the application to catastrophic SQL injection attacks. Malicious input like `message = "'); DROP TABLE logs; --"` would execute arbitrary commands, risking data loss or theft.  

**Root Cause**:  
Using string interpolation instead of parameterized queries. The design ignores fundamental security principles for user input handling.  

**Impact**:  
Critical security risk. A single vulnerability could compromise the entire database. *High severity*.  

**Fix**:  
Replace string interpolation with parameterized queries:  
```python
# Before (vulnerable)
sql = f"INSERT INTO logs (msg, ts) VALUES ('{message}', {time.time()})"

# After (secure)
CURSOR.execute("INSERT INTO logs (msg, ts) VALUES (?, ?)", (message, time.time()))
```

**Best Practice**:  
*Always use parameterized queries for SQL. Never interpolate user input.*  

---

#### **2. Global State Usage**  
**Issue**:  
Hardcoded global database connection (`CONN`) and cursor (`CURSOR`) variables.  
**Why it matters**:  
Global state makes unit testing impossible (e.g., mocking database operations) and creates hidden dependencies. Changes to globals can break unrelated code.  

**Root Cause**:  
Database operations are scattered without encapsulation. The code violates separation of concerns.  

**Impact**:  
Reduced testability, maintainability, and modularity. *High severity*.  

**Fix**:  
Encapsulate database logic in a class with dependency injection:  
```python
class Logger:
    def __init__(self, conn):
        self.cursor = conn.cursor()
    
    def write_log(self, message):
        self.cursor.execute("INSERT INTO logs (msg, ts) VALUES (?, ?)", (message, time.time()))
        # Never commit here; let caller decide
```

**Best Practice**:  
*Prefer dependency injection over global state to decouple concerns.*  

---

#### **3. Missing Docstring**  
**Issue**:  
Function `write_log` lacks documentation.  
**Why it matters**:  
Developers cannot understand the function’s purpose, parameters, or return value without reading implementation.  

**Root Cause**:  
No documentation culture. The author assumed the function was self-explanatory.  

**Impact**:  
Slower onboarding, increased bugs from misuse, and reduced code quality. *Medium severity*.  

**Fix**:  
Add a clear docstring:  
```python
def write_log(message: str):
    """
    Records a log entry with current timestamp.
    
    Args:
        message: The log message (user-provided string).
    """
    # ... implementation
```

**Best Practice**:  
*Document all public functions with purpose, parameters, and return values.*  

---

#### **4. Conditional Commit Based on Randomness**  
**Issue**:  
Transaction commits are randomized (`random.choice([True, False])`).  
**Why it matters**:  
Non-deterministic commits cause data loss (if not committed) or duplicates (if committed multiple times).  

**Root Cause**:  
Commit logic is tied to irrelevant randomness instead of business rules.  

**Impact**:  
Inconsistent data state, unreliable debugging, and potential data corruption. *High severity*.  

**Fix**:  
Remove randomness and let callers control transactions:  
```python
# Before (vulnerable)
if random.choice([True, False]):
    CONN.commit()

# After (reliable)
# Caller handles commit explicitly:
# logger.write_log("event")
# CONN.commit()  # Only here when ready
```

**Best Practice**:  
*Transactions must be deterministic and explicitly managed by business logic.*  

---

#### **5. Unclear Function Name**  
**Issue**:  
Function named `do_business_logic_but_sql_heavy` uses negative phrasing ("but") and lacks purpose.  
**Why it matters**:  
The name hides the actual behavior, making code harder to understand and maintain.  

**Root Cause**:  
Naming based on implementation details instead of business intent.  

**Impact**:  
Confusion for maintainers, slower debugging, and poor code discoverability. *Medium severity*.  

**Fix**:  
Rename to reflect business logic:  
```python
# Before
def do_business_logic_but_sql_heavy():
    ...

# After
def simulate_user_activity(logger: Logger, log_limit: int = None):
    ...
```

**Best Practice**:  
*Use positive, descriptive names that explain *what* the function does, not *how* it’s implemented.*  

---

#### **6. Swallowed Exceptions**  
**Issue**:  
Catch-all `except` clause silently ignores errors (`except Exception: pass`).  
**Why it matters**:  
Critical failures (e.g., database timeouts) go undetected, masking bugs.  

**Root Cause**:  
Overly broad exception handling instead of specific error handling.  

**Impact**:  
Silent failures lead to undetected system degradation. *High severity*.  

**Fix**:  
Log errors or handle specific exceptions:  
```python
# Before (dangerous)
try:
    CONN.commit()
except Exception:
    pass  # Hides all errors!

# After (safe)
try:
    CONN.commit()
except sqlite3.Error as e:
    logger.error(f"Database commit failed: {e}")
    raise  # Re-raise for caller to handle
```

**Best Practice**:  
*Never swallow exceptions. Log errors and re-raise if appropriate.*  

---

### Summary of Priorities
| **Issue**                     | **Priority** | **Why**                                                                 |
|-------------------------------|--------------|-------------------------------------------------------------------------|
| SQL Injection                 | High         | Critical security risk.                                                 |
| Global State Usage            | High         | Breaks testability and maintainability.                                 |
| Conditional Commit            | High         | Causes data inconsistency.                                              |
| Swallowed Exceptions          | High         | Masks system failures.                                                  |
| Unclear Function Name         | Medium       | Hinders readability and maintainability.                                |
| Missing Docstring             | Medium       | Reduces code quality and onboarding speed.                              |

> **Key Takeaway**: Fix security risks (SQL injection, exception swallowing) and global state first. Then address naming and documentation to improve long-term maintainability. Always prioritize explicit, deterministic behavior over randomness.