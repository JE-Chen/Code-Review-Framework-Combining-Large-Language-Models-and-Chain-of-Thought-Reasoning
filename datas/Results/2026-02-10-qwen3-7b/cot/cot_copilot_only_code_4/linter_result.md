### Linter Messages

1. **rule_id**: no-exception-handling  
   **severity**: error  
   **message**: The code returns -1 in the Exception case without proper handling.  
   **line**: 13  
   **suggestion**: Handle the Exception case with a meaningful return value.

2. **rule_id**: no-specific-exception-handling  
   **severity**: error  
   **message**: The code uses a broad Exception catch-all.  
   **line**: 11  
   **suggestion**: Handle specific exceptions like ValueError and other exceptions.

3. **rule_id**: no-exception-handling  
   **severity**: error  
   **message**: The code returns different values based on exceptions without proper handling.  
   **line**: 10  
   **suggestion**: Return consistent values for different exceptions.

4. **rule_id**: no-exception-handling  
   **severity**: error  
   **message**: The code returns 0 in the Exception case without proper handling.  
   **line**: 14  
   **suggestion**: Handle the Exception case with a meaningful return value.

5. **rule_id**: no-exception-handling  
   **severity**: error  
   **message**: The code returns None in the Exception case without proper handling.  
   **line**: 19  
   **suggestion**: Handle the Exception case with a meaningful return value.