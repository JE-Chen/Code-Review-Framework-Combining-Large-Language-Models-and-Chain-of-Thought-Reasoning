### Title
Examples of Common Coding Anti-Patterns and Best Practices

### Overview
This code snippet showcases various common coding anti-patterns and best practices, including functions with side effects, mutable default arguments, modifying input parameters, and more.

### Detailed Explanation

#### Function: `add_item`
**Purpose**: Appends an item to a list and returns the modified list.
**Inputs**: An item and an optional container list (default is an empty list).
**Outputs**: The modified container list.
**Key Components**: List comprehension (`container.append(item)`).
**Assumptions**: No assumptions made about the contents of the container.
**Edge Cases**: If no container is provided, it will always start with an empty list.
**Performance Concerns**: O(1) operation for appending an item to a list.
**Security Concerns**: None.
**Improvements**:
- Avoid using mutable default arguments by setting `container=None` and creating a new list inside the function.
- Document that the function modifies its input.

```python
def add_item(item, container=None):
    if container is None:
        container = []
    container.append(item)
    return container
```

#### Function: `append_global`
**Purpose**: Appends a value to a globally defined list and returns the modified list.
**Inputs**: A value.
**Outputs**: The modified global list.
**Key Components**: Global variable (`shared_list`).
**Assumptions**: The global list exists and is accessible.
**Edge Cases**: None.
**Performance Concerns**: O(1) operation for appending an item to a list.
**Security Concerns**: Can lead to unintended side effects across multiple function calls.
**Improvements**:
- Pass the list as an argument to avoid global state.
- Use thread-safe alternatives if needed.

```python
def append_global(value, shared_list=[]):
    shared_list.append(value)
    return shared_list
```

#### Function: `mutate_input`
**Purpose**: Doubles each element in the input list.
**Inputs**: A list of numbers.
**Outputs**: The modified list.
**Key Components**: In-place modification (`data[i] *= 2`).
**Assumptions**: Input is a list of numbers.
**Edge Cases**: Non-list inputs raise a TypeError.
**Performance Concerns**: O(n) operation where n is the length of the list.
**Security Concerns**: Modifies input directly, which can be dangerous.
**Improvements**:
- Return a new list instead of modifying the input.
- Document that the function mutates its input.

```python
def mutate_input(data):
    return [x * 2 for x in data]
```

#### Function: `nested_conditions`
**Purpose**: Returns a string describing the number based on its value.
**Inputs**: An integer.
**Outputs**: A string describing the number.
**Key Components**: Nested if-else statements.
**Assumptions**: Input is an integer.
**Edge Cases**: Non-integer inputs raise a TypeError.
**Performance Concerns**: Constant time complexity.
**Security Concerns**: None.
**Improvements**:
- Simplify the logic using guards.
- Document the function's purpose and constraints.

```python
def nested_conditions(x):
    if isinstance(x, int):
        if x > 0:
            if x < 10:
                return "small" + (" even" if x % 2 == 0 else " odd") + " positive"
            elif x < 100:
                return "medium positive"
            else:
                return "large positive"
        elif x == 0:
            return "zero"
        else:
            return "negative"
    else:
        raise ValueError("Input must be an integer")
```

#### Function: `risky_division`
**Purpose**: Safely divides two numbers.
**Inputs**: Two numbers.
**Outputs**: The result of division or `None` if an exception occurs.
**Key Components**: Try-except block.
**Assumptions**: Inputs are numbers.
**Edge Cases**: Division by zero raises a ZeroDivisionError.
**Performance Concerns**: Constant time complexity.
**Security Concerns**: None.
**Improvements**:
- Catch specific exceptions instead of generic ones.
- Consider returning a tuple `(result, success)`.

```python
def risky_division(a, b):
    try:
        return a / b, True
    except ZeroDivisionError:
        return None, False
```

#### Function: `inconsistent_return`
**Purpose**: Returns either an integer or a string based on a flag.
**Inputs**: A boolean flag.
**Outputs**: Either 42 or "forty-two".
**Key Components**: Conditional return statement.
**Assumptions**: None.
**Edge Cases**: None.
**Performance Concerns**: Constant time complexity.
**Security Concerns**: None.
**Improvements**:
- Define a consistent return type (e.g., always return a string).

```python
def consistent_return(flag):
    return str(42) if flag else "forty-two"
```

#### Function: `compute_in_loop`
**Purpose**: Computes double the value of each element less than the length of the list.
**Inputs**: A list of integers.
**Outputs**: A list of doubled values.
**Key Components**: Loop with conditional check.
**Assumptions**: Input is a list of integers.
**Edge Cases**: Index out-of-bounds error if input contains non-integers.
**Performance Concerns**: O(n) operation where n is the length of the list.
**Security Concerns**: None.
**Improvements**:
- Ensure all elements are integers before processing.
- Use list comprehension for clarity.

```python
def compute_in_loop(values):
    return [v * 2 for v in values if isinstance(v, int)]
```

#### Code Snippet with Side Effects
**Purpose**: Demonstrates side effects caused by list comprehensions.
**Inputs**: None.
**Outputs**: Prints numbers 0 to 2.
**Key Components**: List comprehension with print statement.
**Assumptions**: None.
**Edge Cases**: None.
**Performance Concerns**: Minimal impact, but demonstrates side effects.
**Security Concerns**: None.
**Improvements**:
- Avoid side effects within comprehension.
- Use explicit loops for side effects.

```python
side_effects = [print(i) for i in range(3)]
```

#### Function: `calculate_area`
**Purpose**: Calculates the area of a circle.
**Inputs**: Radius.
**Outputs**: Area.
**Key Components**: Simple mathematical calculation.
**Assumptions**: Valid radius.
**Edge Cases**: Negative radius raises a ValueError.
**Performance Concerns**: Constant time complexity.
**Security Concerns**: None.
**Improvements**:
- Add a docstring explaining the formula used.

```python
def calculate_area(radius):
    if radius < 0:
        raise ValueError("Radius cannot be negative")
    return 3.14159 * radius * radius
```

#### Function: `run_code`
**Purpose**: Executes a string of code.
**Inputs**: String containing valid Python code.
**Outputs**: Result of executed code.
**Key Components**: `eval`.
**Assumptions**: Valid Python code.
**Edge Cases**: Malformed code raises SyntaxError.
**Performance Concerns**: Depends on the complexity of the code.
**Security Concerns**: High risk due to arbitrary code execution.
**Improvements**:
- Avoid using `eval` and consider safer alternatives like `ast.literal_eval`.

```python
def run_code(code_str):
    return eval(code_str)
```

### Summary
The provided code snippets highlight common pitfalls and best practices in Python programming. By understanding these patterns and applying the suggested improvements, developers can write more robust, maintainable, and secure code.