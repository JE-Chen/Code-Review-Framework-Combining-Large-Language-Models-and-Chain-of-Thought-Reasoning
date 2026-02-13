### Code Review Feedback

- **Readability & Consistency**:  
  - Use consistent indentation (4 spaces) and formatting.  
  - Add docstrings to functions for clarity.  

- **Naming Conventions**:  
  - Improve clarity of `CONN` and `CURSOR` names (e.g., `DB_CONN`).  
  - Refactor `do_business_logic_but_sql_heavy()` to explicit names (e.g., `process_events()`).  

- **Software Engineering Standards**:  
  - Extract `setup()` and `main()` into separate functions for modularity.  
  - Avoid duplicate code in `write_log()` and `read_logs()`.  

- **Logic & Correctness**:  
  - Add validation for `limit` in `read_logs()` to prevent invalid queries.  
  - Ensure `time.time()` is used consistently for timestamps.  

- **Performance & Security**:  
  - Replace `random.choice()` with deterministic values for testing.  
  - Add explicit error handling for `CONN.commit()` failures.  

- **Documentation & Testing**:  
  - Add docstrings to `setup()`, `write_log()`, and `read_logs()`.  
  - Include unit tests for edge cases (e.g., empty logs, invalid limits).  

- **Improvements**:  
  - Simplify `main()` by separating logic into helper functions.  
  - Use `f-strings` for better readability in `read_logs()`.