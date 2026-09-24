- Code Smell Type: Mutable Default Argument
- Problem Location: `def add_item(item, container=[]):`
- Detailed Explanation: In Python, default arguments are evaluated once at definition time, not at execution time. The `container` list is shared across all calls to `add_item` that do not provide their own list. This leads to unexpected behavior where items from previous calls persist in subsequent calls.
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
- Detailed Explanation: The use of `eval()` on an input string is a critical security risk. It allows for the execution of arbitrary code, which could lead to system compromise if `code_str` is sourced from user input.
- Improvement Suggestions: Avoid `eval()` entirely. Use `ast.literal_eval()` for safe evaluation of literals, or implement a specific mapping/parser for the required functionality.
- Priority Level: High

- Code Smell Type: Overly Broad Exception Handling
- Problem Location: `def risky_division(a, b): try: ... except Exception: return None`
- Detailed Explanation: Catching the base `Exception` class hides all errors, including `KeyboardInterrupt`, `SystemExit`, or unexpected `TypeErrors`. This makes debugging difficult as it masks the root cause of failures.
- Improvement Suggestions: Catch only the specific exception expected for this operation:
  ```python
  try:
      return a / b
  except ZeroDivisionError:
      return None
  ```
- Priority Level: Medium

- Code Smell Type: Deeply Nested Conditionals (Arrow Anti-pattern)
- Problem Location: `def nested_conditions(x):`
- Detailed Explanation: The function uses multiple levels of nested `if/else` blocks. This increases cognitive load, makes the logic harder to follow, and complicates testing and maintenance.
- Improvement Suggestions: Use "Guard Clauses" to return early and flatten the structure.
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
- Detailed Explanation: The function returns an `int` in one branch and a `str` in another. This forces the caller to perform type checking before using the result, increasing the likelihood of `TypeError` at runtime.
- Improvement Suggestions: Ensure the function returns a consistent type (e.g., always a string or always an integer).
- Priority Level: Medium

- Code Smell Type: Side Effects in List Comprehension
- Problem Location: `side_effects = [print(i) for i in range(3)]`
- Detailed Explanation: List comprehensions are intended for creating lists. Using them to trigger side effects (like `print`) is a misuse of the construct and creates a list of `None` values in memory that is immediately discarded.
- Improvement Suggestions: Use a standard `for` loop for side effects.
- Priority Level: Low