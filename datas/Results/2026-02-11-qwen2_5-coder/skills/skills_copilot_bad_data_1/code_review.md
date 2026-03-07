## Diff #1

### Summary
This PR introduces several functions with various issues related to side effects, mutable default arguments, and inconsistent return types. The functions are designed to demonstrate common pitfalls in Python programming.

### Linting Issues
- **PEP8 E701**: Multiple statements on one line. Found in lines 3, 6, 9, 12, 15, 18, 21, 24, and 27.
- **PEP8 W503**: Line break occurred before a binary operator. Found in lines 3, 6, 9, 12, 15, 18, 21, 24, and 27.

### Code Smells
- **Mutable Default Argument**: The function `add_item` uses a mutable default argument (`container=[]`). This leads to unexpected shared state across function calls. Instead, use `None` as the default value and create the mutable object inside the function.
  ```python
  def add_item(item, container=None):
      if container is None:
          container = []
      container.append(item)
      return container
  ```
- **Side Effects**: Functions like `append_global` modify global state without documentation. Avoid modifying global state unless it is clearly documented and expected.
  ```python
  def append_global(value, shared_list=[]):
      shared_list.append(value)
      return shared_list
  ```
- **Inconsistent Return Types**: The function `inconsistent_return` returns integers and strings, which increases the burden on callers. Ensure consistent return types.
  ```python
  def inconsistent_return(flag):
      if flag:
          return 42
      else:
          return 42  # Return type is now consistent
  ```
- **Unnecessary Work Inside Loops**: The function `compute_in_loop` has an unnecessary check `if v < len(values)`. This condition is always true since `v` is iterating over `values`.
  ```python
  def compute_in_loop(values):
      results = []
      for v in values:
          results.append(v * 2)
      return results
  ```
- **Premature Optimization**: The function `risky_division` catches all exceptions, including `ZeroDivisionError`, which hides important error information. Handle specific exceptions appropriately.
  ```python
  def risky_division(a, b):
      if b == 0:
          raise ValueError("Cannot divide by zero")
      return a / b
  ```

## Diff #2

### Summary
This PR contains additional functions demonstrating various coding anti-patterns.

### Linting Issues
- **PEP8 E701**: Multiple statements on one line. Found in lines 3, 6, 9, 12, 15, 18, 21, 24, and 27.
- **PEP8 W503**: Line break occurred before a binary operator. Found in lines 3, 6, 9, 12, 15, 18, 21, 24, and 27.

### Code Smells
- **Implicit Truthiness**: The function `nested_conditions` relies on implicit truthiness, which can lead to subtle bugs. Use explicit comparisons.
  ```python
  def nested_conditions(x):
      if x > 0:
          if x < 10:
              if x % 2 == 0:
                  return "small even positive"
              else:
                  return "small odd positive"
          elif x < 100:
              return "medium positive"
          else:
              return "large positive"
      elif x == 0:
          return "zero"
      else:
          return "negative"
  ```
- **Shared Mutable State**: The function `run_code` uses `eval`, which can introduce serious security risks. Avoid using `eval`, `exec`, or dynamic code execution unless there is a strong justification.
  ```python
  def run_code(code_str):
      return eval(code_str)
  ```
- **Unnecessary Side Effects**: The list comprehension `side_effects` has unnecessary side effects. Use explicit loops when side effects are required.
  ```python
  side_effects = []
  for i in range(3):
      print(i)
      side_effects.append(i)
  ```
- **Overly Complex Function**: The function `calculate_area` has a simple calculation but could benefit from clearer naming or breaking down into smaller functions.
  ```python
  def calculate_area(radius):
      pi = 3.14159
      return pi * radius * radius
  ```