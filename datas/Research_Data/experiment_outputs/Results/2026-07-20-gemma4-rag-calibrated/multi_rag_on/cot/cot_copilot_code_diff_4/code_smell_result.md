- Code Smell Type: SQL Injection Vulnerability
- Problem Location: 
  `cursorThing.execute("INSERT INTO users(name, age) VALUES('" + name + "', " + str(age) + ")")`
  `cursorThing.execute("INSERT INTO users(name, age) VALUES('" + anotherName + "', " + str(anotherAge) + ")")`
- Detailed Explanation: The code uses string concatenation to build SQL queries. This is a critical security flaw that allows SQL Injection attacks. If the `name` variable were to come from user input, an attacker could manipulate the database structure or leak sensitive data.
- Improvement Suggestions: Use parameterized queries (prepared statements) provided by the `sqlite3` library. Replace the concatenation with `cursorThing.execute("INSERT INTO users(name, age) VALUES(?, ?)", (name, age))`.
- Priority Level: High

- Code Smell Type: Violation of Single Responsibility Principle (God Function)
- Problem Location: `def functionThatDoesTooManyThingsAndIsHardToRead():`
- Detailed Explanation: The function handles database connection, schema creation, data insertion, and data retrieval/reporting all in one block. This makes the code difficult to test, reuse, or maintain. If the insertion logic fails, the retrieval logic is still coupled to it.
- Improvement Suggestions: Refactor the code into smaller, focused functions: `init_db()`, `add_user(name, age)`, and `print_users()`.
- Priority Level: High

- Code Smell Type: Unclear Naming & Poor Consistency
- Problem Location: `cursorThing`, `functionThatDoesTooManyThingsAndIsHardToRead`, `anotherName`, `anotherAge`
- Detailed Explanation: Variable and function names are either non-descriptive (`cursorThing`), overly verbose/self-deprecating (`functionThatDoesTooManyThings...`), or inconsistent (mixing `name` with `anotherName`). This violates the naming convention rules for semantic clarity.
- Improvement Suggestions: Rename `cursorThing` to `cursor`, the main function to `main()` or `run_user_demo()`, and use a loop or a list of tuples to handle multiple users instead of creating `anotherName` variables.
- Priority Level: Medium

- Code Smell Type: Improper Exception Handling (Silent Failures)
- Problem Location: 
  `except Exception as e: print("Something happened but I will ignore:", e)`
  `except: print("查詢失敗但我不在乎")`
- Detailed Explanation: The code catches all exceptions (including `BareExcept`) and simply prints a message without handling the error or re-raising it. This hides bugs and makes debugging in production nearly impossible.
- Improvement Suggestions: Catch specific exceptions (e.g., `sqlite3.Error`). Implement proper logging instead of `print` statements, and ensure the application fails gracefully or recovers correctly.
- Priority Level: Medium

- Code Smell Type: Use of Global State
- Problem Location: `global conn, cursorThing`
- Detailed Explanation: Relying on global variables for database connections creates tight coupling and makes the code thread-unsafe and difficult to test in isolation.
- Improvement Suggestions: Pass the connection or cursor as arguments to functions, or encapsulate the database logic within a class.
- Priority Level: Medium