- Code Smell Type: Mutable Default Argument
- Problem Location: `def add_item(item, container=[]):`
- Detailed Explanation: In Python, default arguments are evaluated once at definition time. The `container` list is shared across all calls to `add_item` that do not provide their own list, leading to unexpected state accumulation and bugs.
- Improvement Suggestions: Use `None` as the default value and initialize the list inside the function: `def add_item(item, container=None): if container is None: container = []`.
- Priority Level: High

- Code Smell Type: Security Risk (Dynamic Code Execution)
- Problem Location: `def run_code(code_str): return eval(code_str)`
- Detailed Explanation: Using `eval` on input strings allows for arbitrary code execution, which is a critical security vulnerability if `code_str` comes from an external or untrusted source.
- Improvement Suggestions: Avoid `eval`. Use safer alternatives like `ast.literal_eval` for data structures or implement a predefined mapping of allowed operations.
- Priority Level: High

- Code Smell Type: Broad Exception Handling
- Problem Location: `def risky_division(a, b): except Exception:`
- Detailed Explanation: Catching the base `Exception` class hides all possible errors (including `KeyboardInterrupt` or `SystemExit` in some contexts, and unrelated `TypeError`s), making debugging difficult and masking the root cause of failures.
- Improvement Suggestions: Catch the specific exception expected: `except ZeroDivisionError:`.
- Priority Level: Medium

- Code Smell Type: Deeply Nested Conditional Logic
- Problem Location: `def nested_conditions(x):`
- Detailed Explanation: The function uses three levels of nested `if/else` blocks. This increases cognitive load and makes the logic harder to follow and maintain.
- Improvement Suggestions: Use guard clauses or a flatter structure to return early. For example: `if x <= 0: return "zero" if x == 0 else "negative"`.
- Priority Level: Medium

- Code Smell Type: Inconsistent Return Types
- Problem Location: `def inconsistent_return(flag):`
- Detailed Explanation: The function returns an `int` in one branch and a `str` in another. This forces the caller to perform type checking before using the result, increasing the risk of runtime `TypeError`s.
- Improvement Suggestions: Ensure the function returns a consistent type (e.g., always a string or always an integer).
- Priority Level: Medium

- Code Smell Type: Shared Mutable State
- Problem Location: `shared_list = []` and `def append_global(value):`
- Detailed Explanation: Modifying a global variable creates hidden coupling between different parts of the application, making the code difficult to test in isolation and prone to race conditions in multi-threaded environments.
- Improvement Suggestions: Encapsulate the state within a class or pass the list explicitly as an argument to the function.
- Priority Level: Medium

- Code Smell Type: Modifying Input Arguments
- Problem Location: `def mutate_input(data):`
- Detailed Explanation: The function modifies the `data` list in place. Callers may not expect their original data to be changed, leading to side effects that are difficult to trace.
- Improvement Suggestions: Create a copy of the data or use a list comprehension to return a new list: `return [x * 2 for x in data]`.
- Priority Level: Medium

- Code Smell Type: List Comprehension for Side Effects
- Problem Location: `side_effects = [print(i) for i in range(3)]`
- Detailed Explanation: List comprehensions are intended for creating new collections. Using them to trigger `print()` calls is a misuse of the construct and creates an unused list of `None` values in memory.
- Improvement Suggestions: Use a standard `for` loop.
- Priority Level: Low

- Code Smell Type: Magic Number
- Problem Location: `return 3.14159 * radius * radius`
- Detailed Explanation: The value `3.14159` is a hard-coded constant. While recognizable as Pi, using magic numbers reduces maintainability and precision.
- Improvement Suggestions: Use `math.pi` from the standard library.
- Priority Level: Low