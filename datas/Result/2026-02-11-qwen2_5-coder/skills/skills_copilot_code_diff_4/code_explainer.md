### Title
A simple Python script to interact with an SQLite database using `sqlite3`.

### Overview
This code is a basic example of how to connect to an SQLite database, create a table, insert data, and query data using Python's `sqlite3` module. The script demonstrates common issues like SQL injection vulnerabilities and lack of proper resource management.

### Detailed Explanation

1. **Imports and Global Variables**
   - `import sqlite3`: Imports the `sqlite3` library for interacting with SQLite databases.
   - `conn = None`: Initializes a connection object to the database.
   - `cursorThing = None`: Initializes a cursor object used for executing SQL commands.

2. **Main Function (`functionThatDoesTooManyThingsAndIsHardToRead`)**
   - Connects to an SQLite database named `test.db`.
   - Creates a table named `users` if it doesn't already exist.
   - Inserts two records into the `users` table.
   - Queries all records from the `users` table and prints them based on their names.
   - Commits changes to the database and closes the connection.

3. **SQL Injection Vulnerability**
   - The script uses string concatenation to build SQL queries, which makes it vulnerable to SQL injection attacks. For example:
     ```python
     cursorThing.execute("INSERT INTO users(name, age) VALUES('" + name + "', " + str(age) + ")")
     ```
   - This can be exploited if user input is not properly sanitized.

4. **Exception Handling**
   - The script catches exceptions but ignores them, which is generally not recommended. For example:
     ```python
     try:
         cursorThing.execute("SELECT * FROM users")
         rows = cursorThing.fetchall()
         # ...
     except:
         print("查詢失敗但我不在乎")
     ```

5. **Resource Management**
   - The database connection is closed at the end, but there's no error handling if closing the connection fails.

### Assumptions and Edge Cases
- Assumes the `test.db` file exists or can be created.
- Does not handle potential errors when inserting or querying data.

### Possible Errors
- SQL injection if user input is used without sanitization.
- Exceptions during database operations that are ignored.
- Resource leaks if connection closing fails.

### Performance or Security Concerns
- Inefficient use of resources due to lack of context managers for database connections.
- Potential denial-of-service (DoS) risks due to improper exception handling.

### Suggested Improvements
1. **Use Parameterized Queries**
   - Replace string concatenation with parameterized queries to prevent SQL injection:
     ```python
     cursorThing.execute("INSERT INTO users(name, age) VALUES(?, ?)", (name, age))
     ```

2. **Proper Error Handling**
   - Catch specific exceptions and log or handle them appropriately:
     ```python
     try:
         cursorThing.execute("SELECT * FROM users")
         rows = cursorThing.fetchall()
     except sqlite3.Error as e:
         print(f"Database error: {e}")
     ```

3. **Context Managers for Database Connections**
   - Use `with` statements to manage database connections and cursors automatically:
     ```python
     with sqlite3.connect("test.db") as conn:
         cursor = conn.cursor()
         # Perform database operations here
     ```

4. **Logging**
   - Add logging instead of printing errors:
     ```python
     import logging
     logging.basicConfig(level=logging.ERROR)
     ```

### Example Usage
```bash
python sql_app.py
```
This will execute the script and print the results of the database operations.