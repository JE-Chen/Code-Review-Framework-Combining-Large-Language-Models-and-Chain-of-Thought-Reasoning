### Code Smell Type: Global Variables
- **Problem Location**: `GLOBAL_TEXT`, `GLOBAL_COUNTER`, `GLOBAL_MODE`
- **Detailed Explanation**: The use of global variables (`GLOBAL_TEXT`, `GLOBAL_COUNTER`, `GLOBAL_MODE`) breaks encapsulation and makes the code difficult to reason about. It also increases the likelihood of side effects and hard-to-find bugs. Each button handler modifies these shared state variables without clear boundaries.
- **Improvement Suggestions**: Encapsulate the state within the `MainWindow` class itself, making the state local to the instance rather than global. Use methods to update the UI based on the internal state of the application.
- **Priority Level**: High

### Code Smell Type: Long Functions
- **Problem Location**: `handle_btn1`, `handle_btn2`, `handle_btn3`
- **Detailed Explanation**: These functions are quite long and perform multiple tasks. They lack cohesion and can be broken down into smaller, more focused functions.
- **Improvement Suggestions**: Refactor each method into smaller functions that each do one thing. For example, `handle_btn1` could have separate functions for appending text, updating the label, and handling empty input.
- **Priority Level**: Medium

### Code Smell Type: Lack of Encapsulation
- **Problem Location**: Direct manipulation of UI elements from global scope
- **Detailed Explanation**: The global scope directly manipulates UI elements like `textArea`. This leads to tight coupling between different parts of the system and makes testing difficult.
- **Improvement Suggestions**: Expose only the necessary methods through the `MainWindow` class's public interface, ensuring that UI interactions happen through well-defined methods.
- **Priority Level**: Medium

### Code Smell Type: Hardcoded Strings and Values
- **Problem Location**: Magic strings ("Add Text", "Show Counter", etc.), hardcoded values (5), and string literals ("Counter is large:", "Even counter:", etc.)
- **Detailed Explanation**: Hardcoding strings and values makes the code less flexible and harder to maintain. If requirements change, you'll need to search through the codebase.
- **Improvement Suggestions**: Use constants or configuration files to store such values and make them easily configurable.
- **Priority Level**: Medium

### Code Smell Type: No Unit Tests
- **Problem Location**: Absence of any unit tests
- **Detailed Explanation**: Without tests, it becomes challenging to ensure that changes don't break existing functionality and makes it difficult to refactor safely.
- **Improvement Suggestions**: Write unit tests for each function, especially edge cases and error handling paths.
- **Priority Level**: High

### Summary
The provided code has several issues that affect its readability, maintainability, and testability. Addressing these will lead to cleaner, more robust code.