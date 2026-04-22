### Code Smell Type: Long Function
- **Problem Location**: The `doSomething` function has a high cyclomatic complexity due to multiple nested conditional statements.
- **Detailed Explanation**: Functions with many branches and nested conditions become difficult to understand and maintain. They also increase the likelihood of bugs.
- **Improvement Suggestions**: Break down the function into smaller, more focused functions each responsible for a single task.
- **Priority Level**: High

### Code Smell Type: Magic Numbers
- **Problem Location**: Values like `10`, `5`, `3`, `2`, `1234`, `42`, `123456789`, `-1` are used without explanation.
- **Detailed Explanation**: Magic numbers make the code less readable and harder to maintain because they lack context.
- **Improvement Suggestions**: Replace magic numbers with named constants or configuration settings.
- **Priority Level**: Medium

### Code Smell Type: Tightly Coupled Data Structures
- **Problem Location**: The `processData` function uses a global `dataList`.
- **Detailed Explanation**: Using global variables or mutable data structures can lead to unexpected side effects and makes testing difficult.
- **Improvement Suggestions**: Pass the data structure as an argument to the function.
- **Priority Level**: Medium

### Code Smell Type: Deeply Nested Conditional Logic
- **Problem Location**: The `main` function contains deeply nested if-else blocks.
- **Detailed Explanation**: Deeply nested logic reduces readability and increases cognitive load.
- **Improvement Suggestions**: Use guard clauses to simplify control flow.
- **Priority Level**: Medium

### Code Smell Type: Lack of Comments
- **Problem Location**: The code lacks comments explaining the purpose of complex sections.
- **Detailed Explanation**: Absence of comments makes the code harder to understand for others.
- **Improvement Suggestions**: Add comments to explain non-obvious logic.
- **Priority Level**: Low

### Code Smell Type: Premature Optimization
- **Problem Location**: No clear indication of performance issues or premature optimization.
- **Detailed Explanation**: Optimizing before identifying bottlenecks can lead to unnecessary complexity.
- **Improvement Suggestions**: Profile the application to find actual performance issues before optimizing.
- **Priority Level**: Low