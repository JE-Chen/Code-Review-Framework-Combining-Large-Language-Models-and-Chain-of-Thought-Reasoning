### Code Smell Analysis

#### Code Smell 1: Long Method
- **Problem Location**: `process` function in `main.py`
- **Detailed Explanation**: The `process` function has a single responsibility but its implementation spans multiple lines, making it harder to understand at a glance. It also performs side effects by modifying the external `data` list.
- **Improvement Suggestions**: Refactor the method into smaller, more focused functions. For example, extract the logic to add keys to the `data` list into a separate function.
- **Priority Level**: Medium

#### Code Smell 2: Magic Numbers
- **Problem Location**: `time.sleep(0.05)` in `_load_random_users` method
- **Detailed Explanation**: The sleep duration is hardcoded, which makes the code less flexible and difficult to adjust without changing the code itself.
- **Improvement Suggestions**: Define these values as constants or configuration parameters.
- **Priority Level**: Low

#### Code Smell 3: Inefficient Use of Resources
- **Problem Location**: Opening and closing files within `_load_from_file` method
- **Detailed Explanation**: The file is opened and closed in each call, which can lead to performance issues when called frequently.
- **Improvement Suggestions**: Consider using context managers (`with` statement) to ensure the file is properly closed after reading.
- **Priority Level**: Low

#### Code Smell 4: Lack of Error Handling
- **Problem Location**: General exception handling in `_load_from_file` method
- **Detailed Explanation**: Catching all exceptions with `except Exception:` hides errors and doesn't provide useful information about what went wrong.
- **Improvement Suggestions**: Catch specific exceptions and log them appropriately.
- **Priority Level**: Medium

#### Code Smell 5: Global Configuration
- **Problem Location**: `CONFIG` dictionary at the top of the file
- **Detailed Explanation**: Using global variables can make the code harder to test and reason about because changes to the global state can affect other parts of the application.
- **Improvement Suggestions**: Pass configuration parameters explicitly through function arguments.
- **Priority Level**: Medium

#### Code Smell 6: Overuse of Class Variables
- **Problem Location**: `UserService` class has a class variable `users`
- **Detailed Explanation**: Class variables can lead to unexpected behavior when shared between instances, especially if they're mutable.
- **Improvement Suggestions**: Use instance variables instead unless there's a compelling reason to use class variables.
- **Priority Level**: Medium

#### Code Smell 7: Lack of Comments
- **Problem Location**: Various parts of the code
- **Detailed Explanation**: Lack of comments makes it hard for others to understand the purpose and intent of the code.
- **Improvement Suggestions**: Add comments to explain complex logic, decisions, or non-obvious operations.
- **Priority Level**: Low

### Summary
The code contains several issues that could impact readability, maintainability, and overall quality. Addressing these code smells will help improve the robustness and scalability of the system.