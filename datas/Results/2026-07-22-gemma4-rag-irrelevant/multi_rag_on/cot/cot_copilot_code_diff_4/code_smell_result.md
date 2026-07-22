- Code Smell Type: SQL Injection Vulnerability
- Problem Location: 
  `cursorThing.execute("INSERT INTO users(name, age) VALUES('" + name + "', " + str(age) + ")")`
- Detailed Explanation: The code uses string concatenation to build SQL queries. This is a critical security flaw that allows an attacker to manipulate the database by injecting malicious SQL commands through the `name` or `age` variables.
- Improvement Suggestions: Use parameterized queries (prepared statements) provided by the `sqlite3` library. Replace the concatenation with: `cursorThing.execute("INSERT INTO users(name, age) VALUES(?, ?)", (name, age))`.
- Priority Level: High

- Code Smell Type: Violation of Single Responsibility Principle (God Function)
- Problem Location: `def functionThatDoesTooManyThingsAndIsHardToRead():`
- Detailed Explanation: The function handles database connection, schema creation, data insertion, and data retrieval/reporting all in one block. This makes the code difficult to test, reuse, or maintain.
- Improvement Suggestions: Decompose the function into smaller, focused functions: `init_db()`, `add_user(name, age)`, and `print_users()`.
- Priority Level: High

- Code Smell Type: Poor Naming Conventions
- Problem Location: `cursorThing`, `functionThatDoesTooManyThingsAndIsHardToRead`, `r`
- Detailed Explanation: Variable and function names are either non-descriptive (`r`), overly verbose/unprofessional (`functionThatDoesTooManyThings...`), or use inconsistent naming styles (`cursorThing` is camelCase, while Python standard PEP 8 suggests snake_case).
- Improvement Suggestions: Rename `cursorThing` to `cursor`, the main function to `manage_user_data()`, and the loop variable `r` to `user_row`.
- Priority Level: Medium

- Code Smell Type: Improper Exception Handling (Silent Failures)
- Problem Location: 
  `except Exception as e: print("Something happened but I will ignore:", e)`
  `except: print("查詢失敗但我不在乎")`
- Detailed Explanation: The code catches all exceptions (including system exits and keyboard interrupts in the second case) and simply prints a message without handling the error or re-raising it. This masks bugs and makes debugging nearly impossible in production.
- Improvement Suggestions: Catch specific exceptions (e.g., `sqlite3.Error`), log the errors using a logging library, and implement a proper recovery or termination strategy.
- Priority Level: Medium

- Code Smell Type: Use of Global State
- Problem Location: `global conn, cursorThing`
- Detailed Explanation: Relying on global variables for database connections creates tight coupling and makes the code thread-unsafe and difficult to test in isolation.
- Improvement Suggestions: Pass the connection or cursor as arguments to functions, or encapsulate the database logic within a class.
- Priority Level: Medium