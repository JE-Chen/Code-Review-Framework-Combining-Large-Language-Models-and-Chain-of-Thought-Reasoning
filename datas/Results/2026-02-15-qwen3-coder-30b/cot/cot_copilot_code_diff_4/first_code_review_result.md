### Code Review Summary

#### 1. **Readability & Consistency**
- Inconsistent indentation and lack of spacing around operators reduce readability.
- No comments to explain logic or purpose of functions or blocks.

#### 2. **Naming Conventions**
- Function name `functionThatDoesTooManyThingsAndIsHardToRead` is too vague and does not reflect its behavior.
- Variables like `cursorThing`, `anotherName`, and `anotherAge` are unclear and non-descriptive.

#### 3. **Software Engineering Standards**
- Function performs multiple unrelated tasks (DB setup, insertion, querying), violating single responsibility principle.
- Global variables (`conn`, `cursorThing`) make code hard to test and reuse.
- Hardcoded values and string concatenation in SQL queries increase risk of errors and SQL injection.

#### 4. **Logic & Correctness**
- Generic exception handling suppresses important error information.
- Useless conditionals (`len(r) > 0`) add no value and reduce clarity.
- Lack of input sanitization makes code vulnerable to SQL injection.

#### 5. **Performance & Security**
- String concatenation for SQL queries poses a major security risk.
- No transaction rollback or cleanup on failure.

#### 6. **Documentation & Testing**
- Missing docstrings or inline comments for function behavior.
- No unit tests provided to verify functionality.

#### 7. **Suggestions**
- Refactor large function into smaller, focused functions.
- Avoid global state and use context managers for DB connections.
- Use parameterized queries to prevent SQL injection.
- Improve naming and add descriptive comments.
- Handle exceptions more specifically and log errors instead of ignoring them.

--- 

**Overall Rating:** ⚠️ Needs Improvement  
This code has several structural and security flaws that need addressing before production use.