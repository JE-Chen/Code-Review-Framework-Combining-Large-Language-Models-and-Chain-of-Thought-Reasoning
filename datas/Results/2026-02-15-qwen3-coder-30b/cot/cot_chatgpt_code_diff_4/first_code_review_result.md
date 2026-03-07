- **Readability & Formatting**  
  - Indentation is consistent but could benefit from aligning multi-line SQL strings for better readability.  
  - Comments are missing; consider adding brief docstrings or inline comments for key functions like `write_log` and `do_business_logic_but_sql_heavy`.

- **Naming Conventions**  
  - Function name `do_business_logic_but_sql_heavy` is unclear and verbose — rename to something more descriptive such as `simulate_user_activity`.  
  - Variables like `i`, `ts`, `msg` are acceptable but can be expanded slightly for clarity (e.g., `log_id`, `timestamp`, `message_text`) in contexts where ambiguity might occur.

- **Modularity & Maintainability**  
  - Hardcoded values (`3`, `LIMIT`, etc.) should be extracted into constants or parameters to improve reusability and testing.  
  - The use of global connection (`CONN`, `CURSOR`) reduces modularity and makes testing harder. Consider passing dependencies explicitly.

- **Logic & Correctness**  
  - SQL injection vulnerability exists in both `write_log` and `read_logs` due to string concatenation instead of parameterized queries.  
  - In `do_business_logic_but_sql_heavy`, unhandled exceptions during commit may hide real failures; logging or raising would improve error visibility.  
  - Randomized behavior in `write_log` and `do_business_logic_but_sql_heavy` introduces inconsistency — make it deterministic for easier debugging and testing.

- **Performance & Security**  
  - Frequent commits inside loops (e.g., in `write_log`) can reduce performance. Committing once after batch operations is preferred.  
  - Using `:memory:` database is fine for demo, but production code should validate and manage DB connections properly.

- **Documentation & Testing**  
  - No docstrings or type hints present. Adding them improves maintainability and understanding.  
  - Lack of unit tests for core logic increases risk of regressions. Suggest mocking the DB and validating outputs.

- **Suggestions**  
  - Replace raw SQL with parameterized queries in `write_log` and `read_logs`.  
  - Extract hardcoded numbers and strings into named constants.  
  - Rename `do_business_logic_but_sql_heavy` for clarity.  
  - Make `setup()` and `main()` more testable by accepting config or DB connection.  
  - Use `try...except` with specific exception types instead of bare `except`.