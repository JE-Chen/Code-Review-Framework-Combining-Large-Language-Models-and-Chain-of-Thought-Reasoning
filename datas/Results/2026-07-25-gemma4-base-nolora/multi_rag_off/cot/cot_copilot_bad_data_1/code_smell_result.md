- Code Smell Type: Mutable Default Argument
- Problem Location: `def add_item(item, container=[]):`
- Detailed Explanation: In Python, default arguments are evaluated only once at the time of function definition. The list `[]` is shared across all calls to `add_item`. If the function is called multiple times without providing a container, items will accumulate from previous calls, leading to unpredictable behavior and bugs.
- Improvement Suggestions: Use `None` as the default value and initialize the list inside the function:
  ```python
  def add_item(item, container=None):
      if container is None:
          container = []
      container.append(item)
      return container
  ```
- Priority Level: High

- Code Smell Type: Security Vulnerability (Arbitrary Code Execution)
- Problem Location: `def run_code(code_str): return eval(code_str)`
- Detailed Explanation: The use of `eval()` on an input string is a critical security risk. It allows for the execution of arbitrary code, which could be used to delete files, steal data, or crash the system if the input is sourced from a user or an external API.
- Improvement Suggestions: Avoid `eval()` entirely. If the goal is to evaluate mathematical expressions, use a safe library like `ast.literal_eval` or a dedicated expression parser.
- Priority Level: High

- Code Smell Type: Overly Broad Exception Handling
- Problem Location: `except Exception: return None` in `risky_division`
- Detailed Explanation: Catching the base `Exception` class is too broad. It suppresses not only the expected `ZeroDivisionError` but also system-level interrupts (like `KeyboardInterrupt` in some versions) or programming errors (like `TypeError` if `a` or `b` are not numbers), making debugging extremely difficult.
- Improvement Suggestions: Catch only the specific exception expected:
  ```python
  try:
      return a / b
  except ZeroDivisionError:
      return None
  ```
- Priority Level: Medium

- Code Smell Type: Deeply Nested Conditionals (Arrow Anti-pattern)
- Problem Location: `def nested_conditions(x):`
- Detailed Explanation: The function uses multiple levels of nested `if/else` blocks. This increases cognitive load, makes the code harder to read, and increases the likelihood of logic errors when modifying the conditions.
- Improvement Suggestions: Use "Guard Clauses" to return early and flatten the structure:
  ```python
  if x == 0: return "zero"
  if x < 0: return "negative"
  if x >= 100: return "large positive"
  if x >= 10: return "medium positive"
  return "small even positive" if x % 2 == 0 else "small odd positive"
  ```
- Priority Level: Medium

- Code Smell Type: Inconsistent Return Types
- Problem Location: `def inconsistent_return(flag):`
- Detailed Explanation: The function returns an `int` in one branch and a `str` in another. This forces the caller to perform type-checking before using the result, which violates the principle of predictability and can lead to `TypeError` at runtime.
- Improvement Suggestions: Ensure the function returns a consistent type (e.g., always a string or always an integer).
- Priority Level: Low

- Code Smell Type: Side Effect in List Comprehension
- Problem Location: `side_effects = [print(i) for i in range(3)]`
- Detailed Explanation: List comprehensions are intended for creating new lists based on existing data. Using them solely to trigger side effects (like `print`) is a misuse of the construct. Furthermore, it creates a list of `None` values in memory that is immediately discarded.
- Improvement Suggestions: Use a standard `for` loop:
  ```python
  for i in range(3):
      print(i)
  ```
- Priority Level: Low