- Code Smell Type: Mutable Default Argument
- Problem Location: `def add_item(item, container=[]):`
- Detailed Explanation: In Python, default arguments are evaluated once at definition time, not at execution time. The list `[]` is shared across all calls to `add_item` that do not provide a `container` argument. This leads to unexpected behavior where subsequent calls accumulate items from previous calls, causing bugs that are difficult to trace.
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
- Detailed Explanation: The use of `eval()` on an input string is a critical security risk. If `code_str` comes from an untrusted source, an attacker can execute arbitrary Python code on the host system, leading to full system compromise.
- Improvement Suggestions: Avoid `eval()` entirely. If the goal is to evaluate mathematical expressions, use a safe library like `ast.literal_eval` or a dedicated expression parser.
- Priority Level: High

- Code Smell Type: Overly Broad Exception Handling
- Problem Location: `def risky_division(a, b): try: ... except Exception: return None`
- Detailed Explanation: Catching the base `Exception` class hides all possible errors, including `KeyboardInterrupt`, `MemoryError`, or `TypeError` (e.g., if `a` is a string). This makes debugging extremely difficult because it masks the root cause of failures.
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
- Detailed Explanation: The function returns an `int` in one branch and a `str` in another. This forces the caller to perform type checking before using the result, increasing the likelihood of `TypeError` at runtime.
- Improvement Suggestions: Ensure the function returns a consistent type. If different types are necessary, use a Type Union (in type hints) or return a structured object/tuple.
- Priority Level: Low