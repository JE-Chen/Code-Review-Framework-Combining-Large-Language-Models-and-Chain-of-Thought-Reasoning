### Linter Messages

1. **rule_id**: `global-variable-usage`  
   **severity**: **warning**  
   **message**: Global variable `USER_COUNT` is used in `add_item`, which is not recommended.  
   **line**: 13  
   **suggestion**: Use an instance variable or pass `USER_COUNT` as a parameter to avoid global scope pollution.  

2. **rule_id**: `no-docstrings`  
   **severity**: **info**  
   **message**: Missing docstrings for critical functions.  
   **line**: 20, 25, 30, 35  
   **suggestion**: Add docstrings to explain function purposes and parameters.  

3. **rule_id**: `logic-unclear`  
   **severity**: **warning**  
   **message**: `get_items` logic is unclear due to implicit mode handling.  
   **line**: 21  
   **suggestion**: Add comments or separate mode handling logic for clarity.  

4. **rule_id**: `parameter-handling`  
   **severity**: **info**  
   **message**: `complex_route` returns default values without explicit validation.  
   **line**: 23  
   **suggestion**: Validate input types and add explicit error handling.  

---

### Summary
The code lacks docstrings and uses global variables, which reduce readability and maintainability. Minor improvements in clarity and documentation are recommended.