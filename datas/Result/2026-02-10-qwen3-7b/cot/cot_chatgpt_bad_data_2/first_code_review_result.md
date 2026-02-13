### Code Review Feedback

- **Readability & Consistency**  
  - Improve line alignment for readability (e.g., `if source == "random":` should be indented consistently).  
  - Add explicit docstrings for functions and classes.  

- **Naming Conventions**  
  - Rename `users` to `user_data` for clarity in context.  
  - Use `user_name` instead of `name` in dictionary keys.  

- **Software Engineering Standards**  
  - Extract `process` into a separate function with explicit parameters.  
  - Add validation for `source` in `load_users`.  

- **Logic & Correctness**  
  - Add boundary checks for `CONFIG["retry"]` in `main`.  
  - Ensure `process` returns `False` when no users are loaded.  

- **Performance & Security**  
  - Avoid unnecessary `time.sleep()` in `_load_random_users`.  
  - Validate `source` input in `load_users`.  

- **Documentation & Testing**  
  - Add docstrings for `process` and `main`.  
  - Include test cases for edge scenarios (e.g., empty users).  

- **Conciseness**  
  - Simplify `process` logic by directly returning `data` or `False`.  

---  
**Score: 9/10**  
**Key Improvements**: Clearer docstrings, consistent naming, and modularized logic.