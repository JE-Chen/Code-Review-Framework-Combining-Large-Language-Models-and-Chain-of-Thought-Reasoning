- Code Smell Type: Mutable Default Argument
- Problem Location: `def add_item(item, container=[]):`
- Detailed Explanation: In Python, default arguments are evaluated once at definition time. The `container` list is shared across all calls to `add_item` that do not provide their own list, leading to unexpected state persistence between function calls.
- Improvement Suggestions: Use `None` as the default value and initialize the list inside the function: `def add_item(item, container=None): if container is None: container = []`.
- Priority Level: High

- Code Smell Type: Security Risk (Dynamic Code Execution)
- Problem Location: `def run_code(code_str): return eval(code_str)`
- Detailed Explanation: The use of `eval` allows for the execution of arbitrary code. If `code_str` comes from an untrusted source, it creates a critical security vulnerability (Remote Code Execution).
- Improvement Suggestions: Avoid `eval`. Use safer alternatives like `ast.literal_eval` for data structures or implement a predefined mapping of allowed operations.
- Priority Level: High

- Code Smell Type: Deeply Nested Conditional Logic
- Problem Location: `def nested_conditions(x):`
- Detailed Explanation: The function uses three levels of nested `if/else` blocks. This increases cognitive load and makes the logic harder to follow and test.
- Improvement Suggestions: Use guard clauses to return early or flatten the logic using `elif` statements to reduce nesting.
- Priority Level: Medium

- Code Smell Type: Inconsistent Return Types
- Problem Location: `def inconsistent_return(flag):` (returns `int` or `str`) and `def risky_division(a, b):` (returns `float` or `None`).
- Detailed Explanation: Returning different types from the same function forces the caller to perform type checking (e.g., `isinstance`) before using the result, which is error-prone and reduces maintainability.
- Improvement Suggestions: Ensure functions return a consistent type. For `risky_division`, consider raising a specific exception or returning a consistent "Null Object" pattern.
- Priority Level: Medium

- Code Smell Type: Shared Mutable State
- Problem Location: `shared_list = []` and `def append_global(value):`
- Detailed Explanation: Modifying a global variable introduces hidden coupling between different parts of the application, making the code difficult to reason about and nearly impossible to unit test in isolation.
- Improvement Suggestions: Encapsulate the state within a class or pass the list explicitly as an argument to the function.
- Priority Level: Medium

- Code Smell Type: Side Effects in List Comprehension
- Problem Location: `side_effects = [print(i) for i in range(3)]`
- Detailed Explanation: List comprehensions are intended for creating collections. Using them to trigger side effects (like `print`) is a misuse of the construct and creates an unused list in memory.
- Improvement Suggestions: Use a standard `for` loop for operations that perform side effects.
- Priority Level: Low

- Code Smell Type: Magic Number
- Problem Location: `return 3.14159 * radius * radius`
- Detailed Explanation: The value `3.14159` is a hard-coded constant. While recognizable as Pi, using magic numbers reduces clarity and makes updates harder.
- Improvement Suggestions: Use `math.pi` from the standard library.
- Priority Level: Low