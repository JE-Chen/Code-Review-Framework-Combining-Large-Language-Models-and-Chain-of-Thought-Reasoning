### ✅ Summary

This Python script demonstrates basic SQLite usage, but it has several critical issues related to **security**, **readability**, **maintainability**, and adherence to best practices. The function does too many things at once and uses unsafe SQL injection-prone patterns.

---

## 🔍 Linter & Code Smell Issues

### 1. ❌ **Global Variables**
```python
conn = None
cursorThing = None
```
- **Why It Matters**: Global state makes testing harder and leads to side effects.
- **Suggestion**: Avoid globals; pass dependencies explicitly or use classes.

---

### 2. ⚠️ **Unsafe String Concatenation for SQL Queries**
```python
cursorThing.execute("INSERT INTO users(name, age) VALUES('" + name + "', " + str(age) + ")")
```
- **Why It Matters**: Vulnerable to SQL injection attacks.
- **Suggestion**: Use parameterized queries (`?` placeholders).

---

### 3. 🧹 **Overly Complex Logic with Nested Conditionals**
```python
if len(r) > 0:
    if r[1] == "Alice":
        ...
    else:
        if r[1] == "Bob":
            ...
```
- **Why It Matters**: Hard to read, debug, and maintain.
- **Suggestion**: Replace nested `if`s with early returns or switch-like logic using dictionaries.

---

### 4. ❗ **Catch-All Exceptions**
```python
except:
    print("查詢失敗但我不在乎")
```
- **Why It Matters**: Silently ignores errors, masking bugs or unexpected behavior.
- **Suggestion**: Catch specific exceptions like `sqlite3.Error`.

---

### 5. 🧱 **Single Function Doing Too Much**
```python
functionThatDoesTooManyThingsAndIsHardToRead()
```
- **Why It Matters**: Violates Single Responsibility Principle — hard to test, reuse, or modify.
- **Suggestion**: Split into smaller functions: setup_db(), insert_users(), fetch_and_print().

---

## ✅ Best Practices Recommendations

| Area | Recommendation |
|------|----------------|
| **Database Access** | Wrap DB operations in context managers or helper classes. |
| **SQL Injection** | Always use parameterized queries. |
| **Error Handling** | Log actual exceptions instead of ignoring them. |
| **Code Structure** | Break large functions into smaller, focused ones. |

---

## 💡 Refactoring Example (Improved Version)

Here's how you might refactor the code:

```python
import sqlite3

def init_db():
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")
    return conn, cursor

def insert_user(cursor, name, age):
    cursor.execute("INSERT INTO users(name, age) VALUES (?, ?)", (name, age))

def fetch_and_print_users(cursor):
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    for row in rows:
        if row[1] == "Alice":
            print("找到 Alice:", row)
        elif row[1] == "Bob":
            print("找到 Bob:", row)
        else:
            print("其他人:", row)

def main():
    conn, cursor = init_db()

    try:
        insert_user(cursor, "Alice", 25)
        insert_user(cursor, "Bob", 30)
        fetch_and_print_users(cursor)
        conn.commit()
    except sqlite3.Error as e:
        print("数据库操作失败:", e)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
```

---

## ✅ Strengths

- Basic understanding of SQLite interaction.
- Some attempt to structure flow from setup to query.

---

## 🛑 Weaknesses

- No error logging or handling.
- Poor security due to raw string interpolation.
- Unorganized logic and lack of modularity.

---

## 📌 Final Notes

The core functionality works, but without addressing security and design flaws, this code should not be used in production or shared widely. Focus on modularizing and securing database interactions first.

Let me know if you'd like help with unit tests or async support next!