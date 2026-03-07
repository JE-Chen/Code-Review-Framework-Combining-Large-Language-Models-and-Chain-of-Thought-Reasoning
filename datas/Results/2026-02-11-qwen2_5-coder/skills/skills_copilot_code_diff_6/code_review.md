### Diff #1

#### Summary
This PR introduces a new Python script named `bad_requests.py`. The script demonstrates poor coding practices such as using global variables, handling exceptions poorly, and performing multiple unrelated operations within a single function. The primary goal seems to be making HTTP requests but lacks proper error handling and modularity.

#### Linting Issues
- **PEP8**: Missing module docstring.
  - *File*: bad_requests.py
  - *Line*: 1
  
- **PEP8**: Global variable names should be all uppercase.
  - *File*: bad_requests.py
  - *Line*: 4, 5
  
- **PEP8**: Function name does not follow snake_case convention.
  - *File*: bad_requests.py
  - *Line*: 7
  
- **PEP8**: Variable names do not follow snake_case convention.
  - *File*: bad_requests.py
  - *Line*: 18

#### Code Smells
- **Global State**: The use of `GLOBAL_SESSION` and `ANOTHER_GLOBAL` as global variables violates the Single Responsibility Principle and makes the code harder to test and debug.
  
- **Long Functions**: `functionThatDoesTooMuchAndIsHardToUnderstand()` contains multiple tasks, including making HTTP requests, printing status codes, and handling exceptions. This breaks the Single Responsibility Principle and makes the function difficult to understand and maintain.

- **Poor Error Handling**: Exceptions are caught and ignored (`except:`), which can hide bugs and make debugging challenging. It's better to log errors or handle them appropriately.

- **Inconsistent Naming**: Variable names like `weirdVariableName` are inconsistent and do not follow PEP8 guidelines. Proper naming improves readability and maintainability.

Recommendations:
1. Move global state out of the script and pass necessary dependencies explicitly to functions.
2. Break down large functions into smaller, more focused functions.
3. Improve exception handling by logging or re-raising exceptions instead of ignoring them.
4. Rename variables to follow PEP8 conventions.