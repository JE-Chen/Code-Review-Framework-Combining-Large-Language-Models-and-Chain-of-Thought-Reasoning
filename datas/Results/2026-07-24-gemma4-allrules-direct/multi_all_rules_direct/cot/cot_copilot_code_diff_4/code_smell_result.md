- Code Smell Type: SQL Injection Vulnerability
- Problem Location: 
  `cursorThing.execute("INSERT INTO users(name, age) VALUES('" + name + "', " + str(age) + ")")`
- Detailed Explanation: The code uses string concatenation to build SQL queries. This is a critical security risk as it allows attackers to inject malicious SQL commands into the database if the input variables (`name`, `age`) were to come from an external source.
- Improvement Suggestions: Use parameterized queries (prepared statements). Replace the concatenation with: `cursorThing.execute("INSERT INTO users(name, age) VALUES(?, ?)", (name, age))`.
- Priority Level: High

- Code Smell Type: Violation of Single Responsibility Principle (SRP) & Poor Naming
- Problem Location: `def functionThatDoesTooManyThingsAndIsHardToRead():`
- Detailed Explanation: The function handles database connection, schema creation, data insertion, and data retrieval/printing all in one block. This makes the code difficult to test, reuse, or maintain. Additionally, the function and variable names (`cursorThing`) are non-descriptive and unprofessional.
- Improvement Suggestions: Split the logic into smaller, focused functions: `init_db()`, `add_user(name, age)`, and `find_users()`. Rename the function and variables to reflect their intent (e.g., `setup_database`, `db_cursor`).
- Priority Level: High

- Code Smell Type: Shared Mutable State (Global Variables)
- Problem Location: `conn = None`, `cursorThing = None` and `global conn, cursorThing`
- Detailed Explanation: Using global variables for database connections introduces hidden coupling and makes the code thread-unsafe and difficult to test. It creates a dependency on the global state of the module.
- Improvement Suggestions: Encapsulate the database logic within a class or pass the connection/cursor as arguments to the functions that need them.
- Priority Level: Medium

- Code Smell Type: Broad Exception Handling
- Problem Location: `except Exception as e:` and `except:`
- Detailed Explanation: Catching all exceptions (including `except:`) hides the actual cause of failures and can mask critical bugs (like `KeyboardInterrupt` or `MemoryError`). The error messages provided are also not helpful for debugging.
- Improvement Suggestions: Catch specific exceptions (e.g., `sqlite3.Error`) and implement proper logging or error propagation instead of just printing "I will ignore".
- Priority Level: Medium

- Code Smell Type: Deeply Nested Conditional Logic
- Problem Location: The `if/else` block inside the `for r in rows:` loop.
- Detailed Explanation: The nested `if` statements increase cognitive load and make the logic harder to follow.
- Improvement Suggestions: Use guard clauses or a mapping dictionary to handle the different user names, or simply flatten the logic using `elif`.
- Priority Level: Low