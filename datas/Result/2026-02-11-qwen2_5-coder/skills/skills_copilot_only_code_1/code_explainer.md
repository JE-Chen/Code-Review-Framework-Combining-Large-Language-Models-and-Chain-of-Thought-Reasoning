### Title
Complex Logic and Readability Issues in Python Code

### Overview
This code snippet demonstrates several issues related to code complexity, readability, and maintainability. It includes nested conditional logic, inconsistent return types, and lack of clarity in function purposes.

### Detailed Explanation
#### Step-by-Step Flow and Components
1. **Function `doSomething`**:
   - Takes 10 parameters (`a` through `j`).
   - Calculates a result based on nested conditions.
   - Returns either a numerical result or a fixed number.

2. **Function `processData`**:
   - Iterates over a list `dataList`.
   - Applies different operations based on whether elements are even or odd.
   - Returns a sum.

3. **Function `main`**:
   - Calls `doSomething` with specific parameters.
   - Prints the result of `doSomething`.
   - Calls `processData` and prints its result.
   - Contains nested conditional logic for printing messages based on integer values.

#### Inputs/Outputs
- **Inputs**: Parameters to `doSomething`, global list `dataList`, and an integer `y`.
- **Outputs**: Results of `doSomething`, `processData`, and printed messages.

#### Key Functions, Classes, or Modules
- `doSomething`: Central function with complex logic.
- `processData`: Iterates over a list and applies transformations.
- `main`: Orchestrates the flow and prints outputs.

### Assumptions, Edge Cases, and Possible Errors
- The purpose of each function is unclear without documentation.
- Edge cases include invalid input types and empty list scenarios.
- Potential errors include division by zero and unexpected side effects.

### Performance or Security Concerns
- Nested conditions can lead to inefficiencies.
- Global state (`dataList`) can cause unexpected behavior.
- Lack of type annotations makes the code harder to understand.

### Suggested Improvements
1. **Simplify `doSomething`**:
   - Break down into smaller functions for each condition.
   - Use more descriptive function names.
   ```python
   def calculate_result(a, b, c, d):
       if d != 0:
           return (a * b * c) / d
       else:
           return 999999

   def default_result(a, b, c, d):
       return a + b + c + d
   ```

2. **Refactor `processData`**:
   - Use list comprehension for clarity.
   ```python
   def process_data(data_list):
       return sum(x * 2 if x % 2 == 0 else x * 3 for x in data_list)
   ```

3. **Improve `main` Functionality**:
   - Extract nested conditions into separate functions.
   ```python
   def check_odd_even(y):
       if y % 2 == 1:
           print("Odd and small")
       else:
           print("Even and small")

   def handle_non_positive(y):
       print("Non-positive")
   ```

### Example Usage
```python
if __name__ == "__main__":
    result = calculate_result(11, 4, 3, 2)
    print("Result:", result)

    processed_value = process_data([1, 2, 3, 4, 5])
    print("Processed:", processed_value)

    y = 5
    check_odd_even(y)
```

By applying these improvements, the code will become more readable, maintainable, and easier to test.