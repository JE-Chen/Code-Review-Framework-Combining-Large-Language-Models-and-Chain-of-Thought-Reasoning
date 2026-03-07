Code Smell Type: Inconsistent Data Structure (Dictionary instead of Class)
Problem Location: Entire order processing logic using dictionary-based order representation (e.g., `create_order`, `calculate_discount`, `process_order`)
Detailed Explanation: Using dictionaries for complex data structures like orders creates multiple issues: 1) Typos cause runtime errors (e.g., `order["customer_type"]` vs `order["customer_type"]`), 2) No type safety or validation, 3) Business logic scattered across functions, 4) Violates encapsulation. This makes code brittle, hard to refactor, and prone to silent failures when keys are misspelled. For example, `process_order` assumes `order["items"]` exists but checks for it later.
Improvement Suggestions: Replace dictionary-based order with a class. Example:
```python
class Order:
    def __init__(self, customer_name, customer_type, items, total_price, created_at):
        self.customer_name = customer_name
        self.customer_type = customer_type
        self.items = items
        self.total_price = total_price
        self.created_at = created_at
        self.paid = False
```
All functions should operate on this object instead of dictionaries.
Priority Level: High

Code Smell Type: Magic Numbers and Strings
Problem Location: `calculate_discount` function (thresholds 1000/500, discount rates 0.2/0.1/0.05)
Detailed Explanation: Hard-coded values lack context and require manual search for changes. If thresholds need adjustment, multiple locations must be updated. Also, the meaning of "1000" isn't clear (e.g., currency units). This reduces maintainability and increases bug risk.
Improvement Suggestions: Define constants with descriptive names:
```python
VIP_THRESHOLD = 1000
VIP_DISCOUNT = 0.2
NORMAL_THRESHOLD = 500
NORMAL_DISCOUNT = 0.05
```
Or better: Use a configuration structure for discount rules.
Priority Level: Medium

Code Smell Type: Side Effects and Mutation of Input
Problem Location: `process_order` mutates input `order` and returns it, plus verbose logging
Detailed Explanation: The function modifies the input dictionary (e.g., adds `total_price`, `final_price`), violating the principle of least surprise. Mutating inputs creates hidden dependencies and complicates debugging. The `verbose` parameter causes side effects (console prints) within business logic, coupling presentation to core functionality.
Improvement Suggestions: 
1. Return a new order object instead of mutating input.
2. Remove `verbose` parameter; move logging to caller or dedicated logger.
3. Separate business logic from presentation.
Priority Level: Medium

Code Smell Type: Inadequate Error Handling
Problem Location: `process_order` prints errors ("No items", "Empty order") but continues processing
Detailed Explanation: The function silently returns invalid state (e.g., order with missing items) after printing. This hides failures from callers, leading to inconsistent data. For example, `process_order` returns an order missing `total_price` if items are missing.
Improvement Suggestions: 
- Raise explicit exceptions (e.g., `InvalidOrderError`) instead of printing.
- Validate inputs at function entry (e.g., `if not order.get("items"): raise InvalidOrderError`).
Priority Level: Medium

Code Smell Type: Lack of Documentation and Tests
Problem Location: No docstrings, minimal comments, zero unit tests
Detailed Explanation: Critical missing documentation prevents understanding of function contracts (e.g., `customer_type` values). Absence of tests makes changes risky and debugging difficult. For example, `calculate_discount`'s behavior isn't verified.
Improvement Suggestions:
1. Add docstrings for all functions/classes.
2. Implement unit tests for key scenarios (e.g., VIP discount, empty items).
3. Use type hints for clarity.
Priority Level: High