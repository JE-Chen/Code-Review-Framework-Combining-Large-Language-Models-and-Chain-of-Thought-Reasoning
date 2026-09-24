- Code Smell Type: Mutable Default Argument
- Problem Location: `def process_items(items=[], verbose=False):`
- Detailed Explanation: In Python, default arguments are evaluated once at definition time. Because `items` is a list, the same list object is shared across all calls to `process_items` that do not provide an explicit `items` argument. This leads to unexpected state persistence between function calls (as seen in `main()` where `output2` will inherit items from the first call).
- Improvement Suggestions: Use `None` as the default value and initialize the list inside the function:
  ```python
  def process_items(items=None, verbose=False):
      if items is None:
          items = []
  ```
- Priority Level: High

- Code Smell Type: Security Vulnerability (Arbitrary Code Execution)
- Problem Location: `return eval(f"{x} * {x}")`
- Detailed Explanation: The use of `eval()` on input that could potentially be controlled by a user is a critical security risk. Even if `x` is expected to be a number, `eval` can execute arbitrary Python code if the input is not strictly validated, leading to Remote Code Execution (RCE).
- Improvement Suggestions: Replace `eval()` with standard arithmetic operators:
  ```python
  return x * x
  ```
- Priority Level: High

- Code Smell Type: Misuse of List Comprehension for Side Effects
- Problem Location: `[results.append(cache[item])]`
- Detailed Explanation: List comprehensions are designed to create new lists. Using them to call a function that modifies a global variable (`results.append`) is a violation of intent. It creates a temporary list in memory that is immediately discarded, which is inefficient and confusing to the reader.
- Improvement Suggestions: Use a simple function call:
  ```python
  results.append(cache[item])
  ```
- Priority Level: Medium

- Code Smell Type: Tight Coupling / Global State Dependency
- Problem Location: `cache = {}`, `results = []` and their usage inside `process_items` and `expensive_compute`.
- Detailed Explanation: The functions rely on global variables for state management. This makes the code difficult to test in isolation, prevents thread safety, and makes the behavior of `process_items` unpredictable because it appends to a global `results` list rather than returning a local result set.
- Improvement Suggestions: Pass the cache as an optional argument to the function or encapsulate the logic within a class. Initialize `results` inside the function scope.
- Priority Level: Medium

- Code Smell Type: Non-Deterministic / Environment-Dependent Logic
- Problem Location: `time.sleep(0.01)`
- Detailed Explanation: Direct calls to `time.sleep` inside business logic make unit tests slow and non-deterministic. It couples the logic to the system clock.
- Improvement Suggestions: If the delay is necessary for a rate limit, abstract the "sleeper" into a provider/interface that can be mocked during testing. If it is unnecessary, remove it.
- Priority Level: Low