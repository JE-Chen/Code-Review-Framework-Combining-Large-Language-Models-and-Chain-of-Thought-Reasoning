### Code Smell Type: SQL Injection Vulnerability
**Problem Location**:  
```python
cursorThing.execute("INSERT INTO users(name, age) VALUES('" + name + "', " + str(age) + ")")
```

**Detailed Explanation**:  
The code constructs SQL queries by directly concatenating user-controlled values (`name`, `age`) into the query string. This creates a severe security vulnerability where malicious input (e.g., `name = "'); DROP TABLE users; --"`) could execute arbitrary SQL commands. Parameterized queries are the industry standard for preventing SQL injection. The current approach violates security best practices and risks data loss or compromise.

**Improvement Suggestions**:  
Replace string concatenation with parameterized queries using `cursor.execute()` with parameters:  
```python
cursorThing.execute("INSERT INTO users(name, age) VALUES(?, ?)", (name, age))
```  
Use `?` placeholders and pass values as a tuple. Always parameterize *all* user inputs in SQL queries.

**Priority Level**: High (Critical security risk)

---

### Code Smell Type: Global Variables
**Problem Location**:  
```python
global conn, cursorThing
conn = sqlite3.connect("test.db")
cursorThing = conn.cursor()
```

**Detailed Explanation**:  
Global state (`conn`, `cursorThing`) creates hidden dependencies, makes code non-reusable, and complicates testing. Functions relying on globals cannot be tested in isolation, as they depend on external state. This violates the Single Responsibility Principle and leads to fragile code where changes to globals break unrelated functionality.

**Improvement Suggestions**:  
Pass database connections as explicit dependencies:  
```python
def insert_user(conn, name, age):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users(name, age) VALUES(?, ?)", (name, age))
    conn.commit()
```

**Priority Level**: High (Blocks testability and maintainability)

---

### Code Smell Type: Single Responsibility Principle Violation
**Problem Location**:  
Entire `functionThatDoesTooManyThingsAndIsHardToRead()` function.

**Detailed Explanation**:  
This function creates a table, inserts records, queries data, and prints results. It handles database setup, data operations, and output logic. This makes the function long, complex, and impossible to reuse. Each responsibility should be in its own function (e.g., `create_database()`, `insert_user()`, `print_users()`), improving readability and testability.

**Improvement Suggestions**:  
Split into focused functions:  
```python
def create_table(conn):
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")

def insert_user(conn, name, age):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users(name, age) VALUES(?, ?)", (name, age))
    conn.commit()

def query_users(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()
```

**Priority Level**: High (Core design flaw)

---

### Code Smell Type: Inadequate Error Handling
**Problem Location**:  
```python
except Exception as e:
    print("Something happened but I will ignore:", e)
```

**Detailed Explanation**:  
Catching all exceptions and silently ignoring them hides bugs (e.g., connection failures, SQL errors). This makes debugging impossible and risks data corruption. Proper error handling should either log the error, re-raise, or handle specific exceptions (e.g., `sqlite3.Error`).

**Improvement Suggestions**:  
Log errors and re-raise:  
```python
except sqlite3.Error as e:
    logging.error("Database error: %s", e)
    raise
```

**Priority Level**: Medium (Reduces reliability)

---

### Code Smell Type: Poor Naming Conventions
**Problem Location**:  
`cursorThing`, `functionThatDoesTooManyThingsAndIsHardToRead()`, `anotherName`, `anotherAge`.

**Detailed Explanation**:  
- `cursorThing` is unclear and unprofessional.  
- The function name is negative and verbose (describes what *not* to do).  
- `anotherName`/`anotherAge` imply a lack of semantic context (e.g., `bob_name` vs. `alice_name`).  
Names should clearly convey *purpose* without ambiguity.

**Improvement Suggestions**:  
- Rename `cursorThing` → `cursor`  
- Rename function → `create_database_and_populate()` (or split as suggested above)  
- Use semantic names: `alice_name`, `bob_age` → `alice`, `bob` (if context is clear)  

**Priority Level**: Medium (Hinders readability)

---

### Code Smell Type: Nested Conditionals
**Problem Location**:  
```python
for r in rows:
    if len(r) > 0:
        if r[1] == "Alice":
            print("找到 Alice:", r)
        else:
            if r[1] == "Bob":
                print("找到 Bob:", r)
            else:
                print("其他人:", r)
```

**Detailed Explanation**:  
Overly nested conditionals (`if`/`else` chains) reduce readability. The `len(r) > 0` check is redundant (a row tuple always has at least one element). This complexity makes the code error-prone and hard to extend (e.g., adding new names requires modifying the logic).

**Improvement Suggestions**:  
Use a simple `if`/`elif` chain or a dictionary-based approach:  
```python
for r in rows:
    if r[1] == "Alice":
        print("找到 Alice:", r)
    elif r[1] == "Bob":
        print("找到 Bob:", r)
    else:
        print("其他人:", r)
```

**Priority Level**: Low (Readability issue)

---

### Code Smell Type: Duplicate Code
**Problem Location**:  
Two nearly identical insert statements:  
```python
cursorThing.execute("INSERT INTO users(name, age) VALUES('" + name + "', " + str(age) + ")")
# ... later ...
cursorThing.execute("INSERT INTO users(name, age) VALUES('" + anotherName + "', " + str(anotherAge) + ")")
```

**Detailed Explanation**:  
The insert pattern is repeated verbatim. If the query structure changes (e.g., adding a new column), it requires fixing two places. This violates the DRY (Don't Repeat Yourself) principle and increases maintenance risk.

**Improvement Suggestions**:  
Extract into a reusable function:  
```python
def insert_user(cursor, name, age):
    cursor.execute("INSERT INTO users(name, age) VALUES(?, ?)", (name, age))
```
Then call it twice:  
```python
insert_user(cursorThing, "Alice", 25)
insert_user(cursorThing, "Bob", 30)
```

**Priority Level**: Low (Minor maintainability impact)

---

### Code Smell Type: Lack of Documentation
**Problem Location**:  
No docstrings or comments explaining the function’s purpose.

**Detailed Explanation**:  
The function’s name is descriptive but the implementation lacks context. Without documentation, new developers cannot understand *why* the function exists or how to use it safely. This impedes onboarding and maintenance.

**Improvement Suggestions**:  
Add a docstring:  
```python
def create_database_and_populate():
    """Creates users table and inserts sample data for demonstration."""
    # ...
```

**Priority Level**: Low (Documentation gap)