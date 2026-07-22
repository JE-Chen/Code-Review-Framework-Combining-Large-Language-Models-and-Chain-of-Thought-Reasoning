### Code Smell Type: Global State
- **Problem Location:** The entire script relies on a global dictionary `GLOBAL_STATE` which holds various mutable data structures and flags.
- **Detailed Explanation:** Using global state makes the code hard to reason about because it can be modified from anywhere in the application at any time. This leads to unpredictable behavior, difficulty in debugging, and issues related to thread safety and concurrent execution.
- **Improvement Suggestions:** Encapsulate the state within classes or modules and pass dependencies explicitly where needed. Use dependency injection or other design patterns to manage state transitions.
- **Priority Level:** High

### Code Smell Type: Magic Numbers
- **Problem Location:** Several values like `21`, `77`, and `0` are hardcoded without explanation.
- **Detailed Explanation:** Hardcoded numbers make the code less readable and harder to maintain. They also increase the risk of errors when these values need to be changed.
- **Improvement Suggestions:** Define constants or use configuration files to store such values.
- **Priority Level:** Medium

### Code Smell Type: Long Function
- **Problem Location:** The `process_items` function has a significant number of lines and complex conditional logic.
- **Detailed Explanation:** Functions with many lines of code are harder to understand, debug, and test. They also violate the Single Responsibility Principle.
- **Improvement Suggestions:** Break down the function into smaller, more focused functions each responsible for a single task.
- **Priority Level:** Medium

### Code Smell Type: Lack of Abstraction
- **Problem Location:** There's no clear separation between initialization, processing, and state manipulation.
- **Detailed Explanation:** Absence of abstractions makes the code harder to read and reuse. It also increases the likelihood of introducing bugs.
- **Improvement Suggestions:** Introduce classes or functions that encapsulate specific behaviors.
- **Priority Level:** Medium

### Code Smell Type: Inefficient Data Structures
- **Problem Location:** The list comprehension in `init_data` could be optimized for larger datasets.
- **Detailed Explanation:** Unnecessary memory usage and slower operations can impact performance, especially with large datasets.
- **Improvement Suggestions:** Consider using generators or more efficient data structures if applicable.
- **Priority Level:** Low

### Code Smell Type: Missing Error Handling
- **Problem Location:** No error handling is performed in the code.
- **Detailed Explanation:** Lack of error handling can lead to crashes or unexpected behavior under certain circumstances.
- **Improvement Suggestions:** Add try-except blocks around critical sections of code to handle exceptions gracefully.
- **Priority Level:** Medium