### Code Smell Type: Long Function
- **Problem Location**: `DataPipeline.run` method
- **Detailed Explanation**: The `run` method contains nested loops and conditional checks, making it difficult to understand and maintain. It also violates the Single Responsibility Principle by handling both the iteration over steps and the processing logic.
- **Improvement Suggestions**: Refactor the `run` method into smaller, more focused methods. Each method should handle a specific aspect of the pipeline execution.
- **Priority Level**: High

### Code Smell Type: Magic Numbers
- **Problem Location**: Multiple places in the code (e.g., `NumberProcessor.process`, `GLOBAL_CONFIG`)
- **Detailed Explanation**: The use of hardcoded numbers without explanation makes the code harder to read and maintain. These values could change unexpectedly, leading to bugs.
- **Improvement Suggestions**: Replace magic numbers with named constants or configuration variables.
- **Priority Level**: Medium

### Code Smell Type: Global State
- **Problem Location**: `GLOBAL_CONFIG`
- **Detailed Explanation**: The use of global state (`GLOBAL_CONFIG`) can lead to unexpected behavior and difficulties in testing. It couples different parts of the system together.
- **Improvement Suggestions**: Pass the necessary configurations through parameters or use dependency injection.
- **Priority Level**: Medium

### Code Smell Type: Inefficient String Concatenation
- **Problem Location**: `StringProcessor.process`
- **Detailed Explanation**: Using string concatenation inside a loop can be inefficient because strings in Python are immutable. This leads to multiple object creations.
- **Improvement Suggestions**: Use a list to collect characters and join them at the end.
- **Priority Level**: Medium

### Code Smell Type: Complex Conditional Logic
- **Problem Location**: `main` function
- **Detailed Explanation**: The nested if statements make the logic hard to follow and understand. They also increase the risk of logical errors.
- **Improvement Suggestions**: Simplify the conditional logic using early returns or helper functions.
- **Priority Level**: Medium

### Code Smell Type: Lack of Abstraction
- **Problem Location**: Multiple processors (`StringProcessor`, `NumberProcessor`)
- **Detailed Explanation**: While these processors have some abstraction, they still contain complex logic. Encapsulating this logic further would improve maintainability.
- **Improvement Suggestions**: Create smaller, more specialized processors or extract common functionality into utility classes.
- **Priority Level**: Medium

### Code Smell Type: Overuse of Super Call
- **Problem Location**: `BaseProcessor.process` and its subclasses
- **Detailed Explanation**: The frequent use of `super()` suggests that the base class is not doing enough work. This can lead to unnecessary complexity.
- **Improvement Suggestions**: Consider removing the base class or providing default implementations that can be overridden.
- **Priority Level**: Medium