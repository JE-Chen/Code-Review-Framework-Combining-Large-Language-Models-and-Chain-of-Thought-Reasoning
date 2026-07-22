- Code Smell Type: SQL Injection Vulnerability
- Problem Location: 
  `cursorThing.execute("INSERT INTO users(name, age) VALUES('" + name + "', " + str(age) + ")")`
  `cursorThing.execute("INSERT INTO users(name, age) VALUES('" + anotherName + "', " + str(anotherAge) + ")")`
- Detailed Explanation: The code uses string concatenation to build SQL queries. This is a critical security flaw that allows attackers to manipulate the database via SQL injection if the input variables (`name`, `anotherName`) were to come from an external source.
- Improvement Suggestions: Use parameterized queries (prepared statements) provided by the `sqlite3` library. Replace the concatenation with: `cursorThing.execute("INSERT INTO users(name, age) VALUES(?, ?)", (name, age))`.
- Priority Level: High

- Code Smell Type: Violation of Single Responsibility Principle (SRP) / Long Function
- Problem Location: `def functionThatDoesTooManyThingsAndIsHardToRead():`
- Detailed Explanation: The function handles database connection, schema creation, data insertion, and data retrieval/reporting all in one block. This makes the code difficult to test, reuse, or maintain. If one part of the logic changes, the entire function must be modified.
- Improvement Suggestions: Break the function into smaller, focused functions: `init_db()`, `add_user(name, age)`, and `print_users()`.
- Priority Level: High

- Code Smell Type: Unclear Naming & Poor Consistency
- Problem Location: `cursorThing`, `functionThatDoesTooManyThingsAndIsHardToRead`, `anotherName`, `anotherAge`
- Detailed Explanation: Variable and function names are either overly verbose/sarcastic or imprecise. `cursorThing` is non-descriptive, and the function name describes its flaws rather than its purpose. Additionally, the code mixes English and Chinese in print statements, which reduces consistency.
- Improvement Suggestions: Use standard naming conventions (e.g., `cursor`, `setup_database`, `user_name`). Ensure all logs/print statements use a single consistent language.
- Priority Level: Medium

- Code Smell Type: Improper Exception Handling (Silent Failures)
- Problem Location: 
  `except Exception as e: print("Something happened but I will ignore:", e)`
  `except: print("查詢失敗但我不在乎")`
- Detailed Explanation: The code catches all exceptions (including `BareExcept`) and simply prints a message without re-raising the error or handling it. This masks bugs and makes debugging in production nearly impossible.
- Improvement Suggestions: Catch specific exceptions (e.g., `sqlite3.Error`). Implement proper logging and ensure that critical failures stop execution or are handled gracefully.
- Priority Level: Medium

- Code Smell Type: Use of Global State
- Problem Location: `global conn, cursorThing`
- Detailed Explanation: Relying on global variables for database connections creates tight coupling and makes the code thread-unsafe and difficult to unit test.
- Improvement Suggestions: Pass the connection or cursor as arguments to functions, or encapsulate the database logic within a class.
- Priority Level: Medium