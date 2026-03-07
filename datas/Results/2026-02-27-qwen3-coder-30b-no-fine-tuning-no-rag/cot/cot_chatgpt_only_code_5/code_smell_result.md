### Code Smell Type: Global State Mutation
- **Problem Location**: `TransactionStore` class and its use of `records = []`
- **Detailed Explanation**: The `TransactionStore` uses a mutable class-level attribute (`records`) which leads to shared state across all instances of the class. This can cause unintended side effects when multiple services or threads interact with the same store, violating encapsulation principles and making testing harder.
- **Improvement Suggestions**: Replace the class variable `records` with an instance variable initialized in `__init__()`. For example: `self.records = []`.
- **Priority Level**: High

---

### Code Smell Type: Magic Numbers
- **Problem Location**: In `check()` function (`x > 100`)
- **Detailed Explanation**: The number `100` is used directly without explanation or configuration. It's unclear what this value represents, leading to reduced readability and maintainability. If the threshold changes, developers might miss important locations where it’s hardcoded.
- **Improvement Suggestions**: Define a constant like `BIG_TRANSACTION_THRESHOLD = 100` at module level or in a config file, then reference it in the `check()` function.
- **Priority Level**: Medium

---

### Code Smell Type: Duplicated Logic
- **Problem Location**: In both `fn_processTransactions()` and `calculate_stats()`, there are loops over collections that could be abstracted into helper functions.
- **Detailed Explanation**: Both functions perform repetitive operations on lists (`append`, `sort`). These patterns suggest opportunities for refactoring into reusable utility functions to reduce redundancy and improve consistency.
- **Improvement Suggestions**: Extract common logic into private helper methods or utility classes/functions for list processing.
- **Priority Level**: Medium

---

### Code Smell Type: Poor Function Naming
- **Problem Location**: Functions such as `fn_processTransactions`, `print_and_collect`, `calculate_stats`, and `report`
- **Detailed Explanation**: These function names do not clearly communicate their purpose. For example, `print_and_collect` does more than just printing and collecting—it also returns a length array. This ambiguity makes understanding the intent difficult without reading the full body.
- **Improvement Suggestions**: Rename functions to reflect exactly what they do, e.g., `group_transaction_totals`, `format_and_display_transactions`, `compute_statistics`, `display_report`.
- **Priority Level**: Medium

---

### Code Smell Type: Lack of Input Validation
- **Problem Location**: `Analyzer.analyze()` and `fn_processTransactions()`
- **Detailed Explanation**: There is no validation of input parameters. If invalid data is passed to these functions, it may lead to runtime errors or incorrect behavior. For example, `Analyzer.analyze()` assumes non-empty `values` list but doesn’t handle empty inputs gracefully.
- **Improvement Suggestions**: Add checks for empty inputs and raise appropriate exceptions or return default values if needed.
- **Priority Level**: High

---

### Code Smell Type: Tight Coupling
- **Problem Location**: `TransactionService` directly depends on `TransactionStore`
- **Detailed Explanation**: The `TransactionService` tightly couples to `TransactionStore` by using it directly instead of an interface or abstraction. This reduces flexibility and makes mocking harder during unit tests.
- **Improvement Suggestions**: Introduce an interface or base class for transaction storage and inject dependencies via dependency injection or factory pattern.
- **Priority Level**: Medium

---

### Code Smell Type: Inconsistent Return Types
- **Problem Location**: `Analyzer.analyze()` returns different types based on conditionals (`float`, `int`, `float`)
- **Detailed Explanation**: The function returns varying data types depending on the mode parameter. While not strictly wrong, inconsistent return types make it harder to reason about expected outputs and increase complexity for consumers of the method.
- **Improvement Suggestions**: Standardize the return type—perhaps always returning a float or defining a consistent output structure (like a dictionary with keys like `"result"` and `"type"`).
- **Priority Level**: Medium

---

### Code Smell Type: Redundant Operations
- **Problem Location**: Inside `calculate_stats()` — `temp.sort()` followed by accessing elements by index
- **Detailed Explanation**: Sorting a copy of the list and then accessing first/last elements is inefficient compared to using `min()` and `max()` directly. Also, `temp.append(n)` followed by sorting is redundant.
- **Improvement Suggestions**: Use built-in functions like `min()`, `max()`, and `sum()` directly on the input list rather than copying and sorting.
- **Priority Level**: Medium

---

### Code Smell Type: Unused Imports
- **Problem Location**: `import statistics`
- **Detailed Explanation**: Although `statistics` is imported, only `mean`, `median`, and `max` are used from it. However, since `Analyzer.analyze()` already handles this correctly, this isn't necessarily a problem, but it can be considered poor hygiene if unused modules are present.
- **Improvement Suggestions**: Either remove unused imports or keep them if they are part of a larger context where other parts will be added later.
- **Priority Level**: Low

---

### Code Smell Type: No Exception Handling
- **Problem Location**: All functions including `main()`, `print_and_collect`, `calculate_stats`, etc.
- **Detailed Explanation**: There is no error handling in any of the functions. If something goes wrong (e.g., missing keys in transaction dict), the application crashes or behaves unpredictably.
- **Improvement Suggestions**: Wrap critical sections in try-except blocks and add logging or error reporting mechanisms where applicable.
- **Priority Level**: High

---

### Code Smell Type: Implicit Dependency on Data Structure
- **Problem Location**: `fn_processTransactions()` assumes transaction dicts have keys `"user"` and `"amount"`
- **Detailed Explanation**: The code assumes that each item in `lst_transactions` has predefined fields (`"user"`, `"amount"`). If these fields are missing or malformed, unexpected behavior occurs.
- **Improvement Suggestions**: Validate input data before processing, perhaps by checking key existence or using dataclasses/validation libraries.
- **Priority Level**: High

---

### Code Smell Type: Unnecessary Complexity in Formatting
- **Problem Location**: `format_transaction()` function
- **Detailed Explanation**: Concatenating strings manually is error-prone and hard to read. Using f-strings or string templates would improve clarity and reduce chances of bugs.
- **Improvement Suggestions**: Refactor to use f-string formatting or `.join()` for cleaner and safer string construction.
- **Priority Level**: Medium