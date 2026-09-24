- Code Smell Type: Mutable Default Argument
- Problem Location: `def add_item(item, container=[]):`
- Detailed Explanation: In Python, default arguments are evaluated once at definition time. The list `[]` is shared across all calls to `add_item` that do not provide a container, leading to unexpected state persistence between independent function calls.
- Improvement Suggestions: Use `None` as the default value and initialize the list inside the function: `def add_item(item, container=None): if container is None: container = []`.
- Priority Level: High

- Code Smell Type: Security Risk (Dynamic Code Execution)
- Problem Location: `def run_code(code_str): return eval(code_str)`
- Detailed Explanation: The use of `eval()` allows for the execution of arbitrary code. If `code_str` comes from an untrusted source, it creates a critical security vulnerability (Remote Code Execution).
- Improvement Suggestions: Avoid `eval()`. Use safer alternatives like `ast.literal_eval()` for data structures or implement a predefined mapping of allowed operations.
- Priority Level: High

- Code Smell Type: Deeply Nested Conditional Logic
- Problem Location: `def nested_conditions(x):`
- Detailed Explanation: The function uses multiple levels of nested `if/else` blocks. This increases cognitive load, makes the logic harder to follow, and complicates testing.
- Improvement Suggestions: Use guard clauses (early returns) to flatten the structure. For example, handle `x <= 0` first, then handle the positive ranges sequentially.
- Priority Level: Medium

- Code Smell Type: Inconsistent Return Types
- Problem Location: `def inconsistent_return(flag):` (returns `int` or `str`) and `def risky_division(a, b):` (returns `float` or `None`).
- Detailed Explanation: Returning different types from the same function forces the caller to perform type-checking (e.g., `isinstance` or `if result is None`) before using the value, which increases the likelihood of `TypeError` at runtime.
- Improvement Suggestions: Ensure functions return a consistent type. For `risky_division`, consider raising a specific exception or returning a consistent "Null Object" pattern. For `inconsistent_return`, return a consistent type (e.g., always a string).
- Priority Level: Medium

- Code Smell Type: Shared Mutable State
- Problem Location: `shared_list = []` and `def append_global(value):`
- Detailed Explanation: Modifying a global variable creates hidden coupling between different parts of the application. This makes the code difficult to reason about, prevents thread safety, and complicates unit testing.
- Improvement Suggestions: Encapsulate the state within a class or pass the list explicitly as an argument to the function.
- Priority Level: Medium

- Code Smell Type: Side Effects in List Comprehension
- Problem Location: `side_effects = [print(i) for i in range(3)]`
- Detailed Explanation: List comprehensions are intended for creating new collections. Using them solely to trigger side effects (like `print`) is a misuse of the construct and creates an unnecessary list of `None` values in memory.
- Improvement Suggestions: Use a standard `for` loop for executing logic/side effects.
- Priority Level: Low

- Code Smell Type: Input Mutation
- Problem Location: `def mutate_input(data):`
- Detailed Explanation: The function modifies the `data` list in place. Callers may not expect their original list to be changed, which can lead to subtle bugs elsewhere in the program.
- Improvement Suggestions: Create a new list (e.g., using a list comprehension) and return it, or clearly document that the function mutates the input.
- Priority Level: Low