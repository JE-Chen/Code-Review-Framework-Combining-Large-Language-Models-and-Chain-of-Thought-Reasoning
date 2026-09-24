- Code Smell Type: Shared Mutable State (Class-level attribute)
- Problem Location: `class TransactionStore: records = []`
- Detailed Explanation: The `records` list is defined as a class attribute rather than an instance attribute. This means all instances of `TransactionStore` share the same list. In a real-world application or a test suite, this creates hidden coupling where data from one test or session leaks into another, making the code non-thread-safe and difficult to test in isolation.
- Improvement Suggestions: Move the initialization of `records` into an `__init__` method:
  ```python
  class TransactionStore:
      def __init__(self):
          self.records = []
  ```
- Priority Level: High

- Code Smell Type: Unclear/Non-standard Naming
- Problem Location: `def fn_processTransactions(lst_transactions):`
- Detailed Explanation: The function name uses a mix of prefixing (`fn_`) and camelCase (`processTransactions`), which violates PEP 8 standards for Python (which recommends `snake_case`). The prefix `fn_` is redundant as the definition keyword `def` already identifies it as a function.
- Improvement Suggestions: Rename the function to `process_transactions`.
- Priority Level: Low

- Code Smell Type: Inconsistent Return Types / Logic Fragility
- Problem Location: `Analyzer.analyze(data, mode)`
- Detailed Explanation: The method returns `statistics.mean(values)` both when the mode is explicitly "mean" and as a fallback for any unrecognized mode. This implicit behavior can hide bugs where a developer passes an incorrect mode string, and the system silently returns a mean instead of raising an error or returning a clear "not found" indicator.
- Improvement Suggestions: Raise a `ValueError` if an unsupported mode is provided, or use a mapping dictionary to handle the modes explicitly.
- Priority Level: Medium

- Code Smell Type: Magic Numbers / Hard-coded Constants
- Problem Location: `date = tx.get("date", "2026-01-01")` and `if x > 100:`
- Detailed Explanation: The date `"2026-01-01"` and the threshold `100` are "magic" values. They are hard-coded into the logic without explanation, making it difficult to update these business rules globally or understand their significance.
- Improvement Suggestions: Define these as named constants at the top of the module (e.g., `DEFAULT_DATE = "2026-01-01"` and `BIG_TRANSACTION_THRESHOLD = 100`).
- Priority Level: Medium

- Code Smell Type: Unnecessary Work / Inefficient Logic
- Problem Location: `calculate_stats(numbers)`
- Detailed Explanation: The function creates a manual copy of the list using a loop (`for n in numbers: temp.append(n)`) and then sorts the entire list just to find the minimum and maximum values. Sorting takes $O(N \log N)$ time, whereas `min()` and `max()` take $O(N)$.
- Improvement Suggestions: Use Python's built-in `min()`, `max()`, and `sum()` functions directly on the input list.
- Priority Level: Low