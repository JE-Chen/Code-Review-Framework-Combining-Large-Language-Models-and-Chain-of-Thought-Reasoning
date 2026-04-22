### Diff #1

#### Summary
This PR introduces a new Python script named `data_analysis.py`. The script contains a function `functionThatDoesTooMuchAndIsNotClear()` which performs several operations including data creation, manipulation, and printing results. The script also defines two global variables `GLOBAL_DF` and `ANOTHER_GLOBAL`.

#### Linting Issues
- **Global Variable Usage**: The use of global variables (`GLOBAL_DF`, `ANOTHER_GLOBAL`) is generally discouraged. Global state can lead to bugs and make the code harder to test and debug.
  - *File*: `data_analysis.py`
  - *Line*: Multiple lines throughout the script
  
- **Function Name**: The name `functionThatDoesTooMuchAndIsNotClear()` does not accurately describe what the function does. It's too vague and doesn't follow the guideline of reflecting intent rather than implementation details.
  - *File*: `data_analysis.py`
  - *Line*: Line 12

#### Code Smells
- **Long Functions**: The function `functionThatDoesTooMuchAndIsNotClear()` is quite large, performing multiple tasks such as creating data, manipulating it, and printing results. This violates the Single Responsibility Principle.
  - *File*: `data_analysis.py`
  - *Line*: Lines 12-36
  
- **Redundant Operations**: The same operation `GLOBAL_DF["Score"] + random.randint(0, 10)` is performed twice, which is redundant and increases complexity.
  - *File*: `data_analysis.py`
  - *Line*: Lines 17 and 18
  
- **Error Handling**: The error handling (`try-except` block) is overly broad, catching all exceptions without providing any useful information about the error.
  - *File*: `data_analysis.py`
  - *Line*: Lines 24-26
  
- **Hardcoded String Literals**: The string `"我不管錯誤是什麼:"` is hardcoded, which makes the script less flexible and harder to internationalize.
  - *File*: `data_analysis.py`
  - *Line*: Line 25

**Recommendations**:
1. Replace global variables with local variables within functions where possible.
2. Rename `functionThatDoesTooMuchAndIsNotClear()` to something that reflects its intent, such as `analyze_and_print_data()`.
3. Break down the function into smaller, single-purpose functions.
4. Remove redundant operations.
5. Improve error handling to catch specific exceptions and provide meaningful error messages.
6. Consider using configuration or environment variables for strings like `"我不管錯誤是什麼:"".