### Diff #1

#### Summary
This PR contains several code changes, including the introduction of new classes, functions, and modifications to existing ones. The primary goal seems to be organizing and improving the functionality of the existing codebase.

#### Linting Issues
- **File:** transaction_service.py
  - **Line 9:** Trailing comma before closing parenthesis.  
    ```python
    def fn_processTransactions(lst_transactions),
    ```
    **Suggestion:** Remove trailing comma.
    ```python
    def fn_processTransactions(lst_transactions):
    ```

- **File:** transaction_service.py
  - **Line 28:** Trailing comma before closing parenthesis.  
    ```python
    def format_transaction(tx),
    ```
    **Suggestion:** Remove trailing comma.
    ```python
    def format_transaction(tx):
    ```

#### Code Smells
- **Function Overload:**
  - Functions like `fn_processTransactions`, `Analyzer.analyze`, `TransactionStore.add`, `TransactionStore.get_all`, `TransactionService.add_transaction`, `TransactionService.fetch`, `print_and_collect`, and `calculate_stats` perform multiple tasks, violating the Single Responsibility Principle (SRP).
  - **Recommendation:** Refactor these functions into smaller, focused functions.

- **Long Function:**
  - `fn_processTransactions` is quite long and complex, making it hard to understand and test.
  - **Recommendation:** Break down this function into simpler functions, such as one for processing transactions and another for grouping them.

- **Magic Numbers/Strings:**
  - Strings like `"mean"`, `"median"`, `"max"` are used directly without definition. These should ideally be constants or enums for better readability and maintainability.
  - **Recommendation:** Define constants or enums for these strings.

- **Global State:**
  - `TransactionStore` uses class variables (`records`) which can lead to unexpected side effects and make testing difficult.
  - **Recommendation:** Use dependency injection or encapsulate state within objects instead of relying on global variables.