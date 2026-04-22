### Code Smell Type: Global Variables
- **Problem Location**: `GLOBAL_DF` and `ANOTHER_GLOBAL`
- **Detailed Explanation**: The use of global variables (`GLOBAL_DF`, `ANOTHER_GLOBAL`) makes the code difficult to reason about and test. It violates the Single Responsibility Principle and can lead to unexpected side effects if other parts of the code modify these variables.
- **Improvement Suggestions**: Replace global variables with parameters or return values from functions. Encapsulate related data within classes or modules.
- **Priority Level**: High

### Code Smell Type: Long Function
- **Problem Location**: `functionThatDoesTooMuchAndIsNotClear()`
- **Detailed Explanation**: This function performs multiple unrelated tasks such as creating a DataFrame, modifying it, calculating statistics, and printing results. It lacks cohesion and is hard to understand.
- **Improvement Suggestions**: Break down the function into smaller, more focused functions. Each function should have one responsibility.
- **Priority Level**: High

### Code Smell Type: Magic Numbers
- **Problem Location**: `random.randint(0, 10)`
- **Detailed Explanation**: Hardcoded constants like `10` reduce the readability and maintainability of the code. They also make it harder to change the behavior without searching through the codebase.
- **Improvement Suggestions**: Define constants at the top of the module or as parameters to functions.
- **Priority Level**: Low

### Code Smell Type: Unnecessary Exception Handling
- **Problem Location**: `except Exception as e: print("我不管錯誤是什麼:", e)`
- **Detailed Explanation**: Catching all exceptions (`Exception as e`) hides errors and prevents proper debugging. It also makes it impossible to handle different types of exceptions appropriately.
- **Improvement Suggestions**: Catch only the specific exceptions you expect and provide useful error messages or re-raise them.
- **Priority Level**: Medium

### Code Smell Type: Lack of Comments and Documentation
- **Problem Location**: Entire file
- **Detailed Explanation**: The code lacks any documentation or comments explaining its purpose or functionality. This makes it difficult for new developers to understand and maintain.
- **Improvement Suggestions**: Add docstrings for functions and classes, and include inline comments where necessary to explain complex logic.
- **Priority Level**: Medium