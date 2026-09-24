- Code Smell Type: SQL Injection Vulnerability
- Problem Location: 
  `cursorThing.execute("INSERT INTO users(name, age) VALUES('" + name + "', " + str(age) + ")")`
  `cursorThing.execute("INSERT INTO users(name, age) VALUES('" + anotherName + "', " + str(anotherAge) + ")")`
- Detailed Explanation: The code uses string concatenation to build SQL queries. This is a critical security flaw that allows SQL Injection attacks. If the `name` variable were to come from user input, a malicious actor could manipulate the database structure or steal data by injecting SQL commands.
- Improvement Suggestions: Use parameterized queries (prepared statements). Replace the concatenation with placeholders: `cursorThing.execute("INSERT INTO users(name, age) VALUES(?, ?)", (name, age))`.
- Priority Level: High

- Code Smell Type: Violation of Single Responsibility Principle (God Function)
- Problem Location: `def functionThatDoesTooManyThingsAndIsHardToRead():`
- Detailed Explanation: The function handles database connection, schema creation, data insertion, and data retrieval/reporting all in one block. This makes the code difficult to test, reuse, or maintain. If the insertion logic fails, the retrieval logic is still coupled to it.
- Improvement Suggestions: Break the function into smaller, modular functions: `init_db()`, `add_user(name, age)`, and `find_users()`.
- Priority Level: High

- Code Smell Type: Unclear Naming & Poor Consistency
- Problem Location: `cursorThing`, `functionThatDoesTooManyThingsAndIsHardToRead`, `anotherName`, `anotherAge`
- Detailed Explanation: Variable and function names are either non-descriptive (`cursorThing`), overly verbose/informal (`functionThatDoesTooManyThings...`), or inconsistent (`name` vs `anotherName`). This violates the naming convention rules for semantic clarity.
- Improvement Suggestions: Rename `cursorThing` to `cursor`, the main function to `main()` or `run_user_demo()`, and use a loop or a list of tuples to handle multiple users instead of creating `anotherName` variables.
- Priority Level: Medium

- Code Smell Type: Improper Exception Handling (Silent Failures)
- Problem Location: 
  `except Exception as e: print("Something happened but I will ignore:", e)`
  `except: print("查詢失敗但我不在乎")`
- Detailed Explanation: The code catches all exceptions (including the bare `except:`) and simply prints a message without re-raising the error or handling it. This "swallowing" of exceptions makes debugging nearly impossible in production environments as the program continues to run in an unstable state.
- Improvement Suggestions: Catch specific exceptions (e.g., `sqlite3.Error`). Use a logging framework instead of `print`. If the error is fatal (like failing to create the table), the program should stop or return an error code.
- Priority Level: Medium

- Code Smell Type: Use of Global State
- Problem Location: `global conn, cursorThing`
- Detailed Explanation: Relying on global variables for database connections creates tight coupling and makes the code thread-unsafe. It prevents the ability to manage multiple database connections or isolate tests.
- Improvement Suggestions: Pass the connection or cursor as arguments to functions, or encapsulate the database logic within a class.
- Priority Level: Medium