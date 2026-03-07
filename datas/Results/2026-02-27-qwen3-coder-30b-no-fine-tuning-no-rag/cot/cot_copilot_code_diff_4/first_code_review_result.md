### Code Review Summary

- **Readability & Consistency**:  
  - Inconsistent indentation and lack of spacing reduce readability.  
  - Comments are missing or non-descriptive (e.g., `print("Something happened but I will ignore:")`).

- **Naming Conventions**:  
  - Function and variable names are unclear and not descriptive (`functionThatDoesTooManyThingsAndIsHardToRead`, `cursorThing`, `anotherName`).  
  - Use of generic names like `r` for row data reduces clarity.

- **Software Engineering Standards**:  
  - Function does too much (creates table, inserts data, queries, prints results), violating single responsibility principle.  
  - Global variables (`conn`, `cursorThing`) make code harder to test and maintain.  
  - No reuse or modularity — duplicated SQL string concatenation logic.

- **Logic & Correctness**:  
  - SQL injection vulnerability due to string concatenation in queries.  
  - Vague error handling (`except: pass`) hides real issues.  
  - Redundant condition checks (`len(r) > 0` and nested `if` blocks can be simplified).

- **Performance & Security**:  
  - High risk of SQL injection from direct string concatenation.  
  - No use of parameterized queries.  
  - Potential performance issue from unneeded loops and repeated database access.

- **Documentation & Testing**:  
  - Missing docstrings or inline comments explaining purpose or parameters.  
  - No unit tests provided; testing is not easily possible due to global state and tight coupling.

### Suggestions

- Rename `functionThatDoesTooManyThingsAndIsHardToRead` to something more descriptive like `setup_and_query_users`.
- Replace global variables with local ones or proper class encapsulation.
- Avoid string concatenation in SQL — use parameterized queries.
- Simplify conditional logic by removing redundant checks.
- Add specific exception handling instead of bare `except:` clauses.
- Consider splitting logic into smaller functions (e.g., insert, query, display).
- Add basic docstrings and comments to explain behavior and usage.