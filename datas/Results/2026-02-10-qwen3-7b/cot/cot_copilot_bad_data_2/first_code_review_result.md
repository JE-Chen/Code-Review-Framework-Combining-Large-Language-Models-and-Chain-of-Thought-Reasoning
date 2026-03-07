- **Function Naming & Clarity**:  
  - Improve `process_user_input` to `handle_user_input` for clarity.  
  - Rename `secret_behavior` to `toggle_secret_mode` for explicit purpose.  
  - Clarify `check_value` to `validate_value` for better intent.  

- **Modularity & Separation of Concerns**:  
  - Extract `timestamped_message` and `unsafe_eval` into separate functions for better encapsulation.  
  - Move `run_task` to a dedicated function and remove global state.  

- **Security & Risk Mitigation**:  
  - Replace `unsafe_eval` with `eval()` for explicit control (if needed).  
  - Refactor `risky_update` to use `try...except` for better error handling.  

- **Logic & Edge Cases**:  
  - Add explicit checks for empty strings in `process_user_input`.  
  - Document behavior of `hidden_flag` in `secret_behavior`.  

- **Readability & Formatting**:  
  - Use consistent indentation (4 spaces).  
  - Replace inline print statements with structured output (e.g., return values).  

- **Testability**:  
  - Add unit tests for `handle_user_input`, `toggle_secret_mode`, and `validate_value`.  

- **Performance**:  
  - Avoid repeated computations in loops (e.g., `f` and `multiply` could be combined).  

- **Global State**:  
  - Replace global variables with parameters or scoped state where possible.