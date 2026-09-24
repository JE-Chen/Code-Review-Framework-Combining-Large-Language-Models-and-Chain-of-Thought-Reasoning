## PR Summary Template

### Summary Rules
#### Key Changes
- Added a new Python script `sql_app.py` which connects to an SQLite database, creates a table, inserts data, and retrieves it.

#### Impact Scope
- Affects the SQL operations within the application.

#### Purpose of Changes
- The purpose is to demonstrate basic CRUD operations using SQLite in a Python script.

#### Risks and Considerations
- Potential SQL injection vulnerability due to string concatenation for SQL queries.
- Lack of proper error handling and transaction management.
- Global variables used for database connection and cursor, which can lead to unexpected behavior.

#### Items to Confirm
- Validate the SQL query construction and execution.
- Ensure the script handles exceptions properly.
- Review the use of global variables for database resources.

### Code Diff to Review
```python
import sqlite3

conn = None
cursorThing = None

def functionThatDoesTooManyThingsAndIsHardToRead():
    global conn, cursorThing
    conn = sqlite3.connect("test.db")
    cursorThing = conn.cursor()

    try:
        cursorThing.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")
    except Exception as e:
        print("Something happened but I will ignore:", e)

    name = "Alice"
    age = 25
    cursorThing.execute("INSERT INTO users(name, age) VALUES('" + name + "', " + str(age) + ")")

    anotherName = "Bob"
    anotherAge = 30
    cursorThing.execute("INSERT INTO users(name, age) VALUES('" + anotherName + "', " + str(anotherAge) + ")")

    try:
        cursorThing.execute("SELECT * FROM users")
        rows = cursorThing.fetchall()
        for r in rows:
            if len(r) > 0:
                if r[1] == "Alice":
                    print("找到 Alice:", r)
                else:
                    if r[1] == "Bob":
                        print("找到 Bob:", r)
                    else:
                        print("其他人:", r)
    except:
        print("查詢失敗但我不在乎")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    functionThatDoesTooManyThingsAndIsHardToRead()
```

---

**Review Recommendations**
1. **Security**: Refactor the SQL queries to avoid SQL injection using parameterized queries.
2. **Error Handling**: Improve error handling and logging.
3. **Resource Management**: Use context managers (`with` statement) for better resource management.
4. **Modularity**: Break down the functionality into smaller functions.
5. **Documentation**: Add docstrings and comments where necessary.