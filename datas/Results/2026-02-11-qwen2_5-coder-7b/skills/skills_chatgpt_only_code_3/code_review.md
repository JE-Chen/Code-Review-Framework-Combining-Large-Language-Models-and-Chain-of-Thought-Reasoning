### Diff #1

#### Summary
This diff introduces a new Python script that handles order creation, processing, logging, and printing. The script defines functions for creating orders, calculating discounts, processing orders, and logging orders using different loggers.

#### Linting Issues
- **PEP8 Violation**: Lines exceed the maximum length of 79 characters.
  - **File**: `<filename>.py`
  - **Line**: 
    - Line 4: `order = {}`
    - Line 6: `discount = 0`
    - Line 10: `return order`
    - Line 17: `return discount`
    - Line 28: `print("No items")`
    - Line 32: `print("Empty order")`
    - Line 38: `for item in order["items"]:`
    - Line 42: `order["total_price"] = total`
    - Line 44: `order["final_price"] = final_price`
    - Line 45: `order["processed_at"] = now`
    - Line 52: `print("Customer:", order["customer_name"])`
    - Line 53: `print("Type:", order["customer_type"])`
    - Line 54: `print("Total:", order["total_price"])`
    - Line 55: `print("Final:", order.get("final_price", order["total_price"]))`
    - Line 60: `print("[FILE]", text)`
    - Line 62: `print("[CONSOLE]", text)`
    - Line 67: `logger.write("Order from " + order["customer_name"])`
    - Line 71: `log_order(processed, logger1)`
    - Line 72: `log_order(processed, logger2)`

- **Unused Import**: The `datetime` import at the top is not used within the script.
  - **File**: `<filename>.py`
  - **Line**: `import datetime`

#### Code Smells
- **Long Functions**: The `process_order` function has a high cognitive complexity due to nested conditions and loops.
  - **Issue**: The function contains multiple conditional checks and updates the order dictionary directly, making it hard to follow the flow of execution.
  - **Recommendation**: Refactor the function into smaller, more focused functions to improve readability and maintainability.

- **Magic Numbers**: The discount thresholds (e.g., 1000, 500) are hardcoded without clear explanations.
  - **Issue**: These values are difficult to understand and modify without context.
  - **Recommendation**: Define these constants as named variables at the beginning of the script or use configuration settings.

- **Potential Side Effects**: The `process_order` function modifies the input `order` dictionary directly.
  - **Issue**: This can lead to unexpected behavior when calling the function multiple times with the same order object.
  - **Recommendation**: Consider returning a new dictionary instead of modifying the existing one.