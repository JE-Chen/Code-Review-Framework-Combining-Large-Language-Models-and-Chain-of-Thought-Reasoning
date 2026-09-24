- Code Smell Type: SQL Injection Vulnerability
- Problem Location: 
  `cursorThing.execute("INSERT INTO users(name, age) VALUES('" + name + "', " + str(age) + ")")`
  `cursorThing.execute("INSERT INTO users(name, age) VALUES('" + anotherName + "', " + str(anotherAge) + ")")`
- Detailed Explanation: The code uses string concatenation to build SQL queries. This is a critical security flaw that allows SQL Injection attacks. If the `name` variable were to come from user input, an attacker could manipulate the database structure or steal data by injecting malicious SQL commands.
- Improvement Suggestions: Use parameterized queries (prepared statements). Replace the concatenation with placeholders: `cursorThing.execute("INSERT INTO users(name, age) VALUES(?, ?)", (name, age))`.
- Priority Level: High

- Code Smell Type: Violation of Single Responsibility Principle (SRP) / Long Function
- Problem Location: `def functionThatDoesTooManyThingsAndIsHardToRead():`
- Detailed Explanation: The function handles database connection, schema creation, data insertion, and data retrieval/reporting all in one block. This makes the code difficult to test, reuse, or maintain. If the insertion logic fails, the retrieval logic still attempts to run, and the connection management is tied to the business logic.
- Improvement Suggestions: Break the function into smaller, focused functions: `init_db()`, `add_user(name, age)`, and `print_users()`.
- Priority Level: High

- Code Smell Type: Unclear/Non-Standard Naming
- Problem Location: `cursorThing`, `functionThatDoesTooManyThingsAndIsHardToRead`, `anotherName`, `anotherAge`
- Detailed Explanation: Variable and function names are either overly verbose/sarcastic or imprecise. `cursorThing` is vague, and the function name describes its own flaws rather than its purpose. This violates professional coding standards and reduces readability.
- Improvement Suggestions: Use descriptive, semantic names: `cursor`, `setup_and_populate_users()`, `user_name`, and `user_age`.
- Priority Level: Medium

- Code Smell Type: Poor Exception Handling (Silent Failures)
- Problem Location: 
  `except Exception as e: print("Something happened but I will ignore:", e)`
  `except: print("查詢失敗但我不在乎")`
- Detailed Explanation: The code catches generic exceptions and simply prints a message without handling the error or re-raising it. This "swallowing" of exceptions makes debugging nearly impossible in production environments because the program continues to execute in an unstable state.
- Improvement Suggestions: Catch specific exceptions (e.g., `sqlite3.Error`). Implement proper logging instead of `print` statements, and decide whether the application should crash or recover based on the error type.
- Priority Level: Medium

- Code Smell Type: Use of Global State
- Problem Location: `global conn, cursorThing`
- Detailed Explanation: Using global variables for database connections creates tight coupling and makes the code thread-unsafe. It prevents the ability to manage multiple database connections or run tests in parallel.
- Improvement Suggestions: Pass the connection or cursor as arguments to functions, or encapsulate the database logic within a class (e.g., `DatabaseManager`).
- Priority Level: Medium