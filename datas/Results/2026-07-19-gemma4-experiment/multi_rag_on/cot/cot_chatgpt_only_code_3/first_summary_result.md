This code review is conducted based on the provided global rules.

### 1. Readability & Consistency
- **Formatting:** The code is generally well-formatted and follows standard Python indentation.
- **Consistency:** The use of `print` statements for both business logic errors (e.g., "No items") and debugging (`verbose=True`) is inconsistent. Business logic errors should ideally be handled via exceptions or a dedicated logging system.

### 2. Naming Conventions
- **Descriptive Names:** Variable and function names (e.g., `calculate_discount`, `process_order`) are clear and descriptive.
- **Semantic Clarity:** The naming is consistent across the codebase.

### 3. Software Engineering Standards
- **Modularity:** The code is split into functions and classes, but there are opportunities for better abstraction:
    - **Data Structures:** Using a `dict` for an `Order` is error-prone. A `dataclass` or `NamedTuple` would provide better type safety and prevent `KeyError` exceptions.
    - **Polymorphism:** The `log_order` function uses `hasattr` to check for `log` or `write` methods. This is a "leaky abstraction." A common `Logger` interface (Abstract Base Class) should be defined so that all loggers implement the same method (e.g., `.log()`).
- **DRY (Don't Repeat Yourself):** The `calculate_discount` function contains repetitive `if/elif` blocks for `vip` and `normal` types. This could be refactored into a lookup table (dictionary) of thresholds and rates.

### 4. Logic & Correctness
- **Redundant Parameter:** In `create_order`, `total_price` is passed as an argument, but it is completely overwritten in `process_order` by summing the items. This makes the initial parameter misleading and unnecessary.
- **Boundary Conditions:**
    - The `calculate_discount` logic uses `> 1000` and `> 500`. If a total is exactly `1000` or `500`, it falls into the lower discount bracket. Ensure this aligns with business requirements.
- **Exception Handling:** There is no error handling for missing keys in the `order` dictionary (e.g., if `customer_name` is missing, `log_order` will crash).

### 5. Performance & Security
- **Performance:** No significant bottlenecks identified for the current scale.
- **Security:** No external inputs are processed, so there are no immediate injection risks. However, the use of `print` for logging in a production environment is generally discouraged.

### 6. Documentation & Testing
- **Documentation:** The code lacks docstrings for functions and classes. It is unclear what the expected types for `items` are without reading the `main()` implementation.
- **Testing:** No unit tests are provided. The `main()` function serves as a manual smoke test, but automated tests are needed to verify discount brackets and order processing.

---

### Summary of Recommendations

| Category | Issue | Recommendation |
| :--- | :--- | :--- |
| **Architecture** | `log_order` uses `hasattr` checks. | Implement a `Logger` base class/interface. |
| **Architecture** | Order is represented as a `dict`. | Use a `dataclass` for `Order`. |
| **Logic** | `total_price` passed to `create_order` is ignored. | Remove `total_price` from `create_order` arguments. |
| **Maintainability** | Hardcoded discount logic. | Move discount rates to a configuration mapping. |
| **Testing** | No automated tests. | Add unit tests for `calculate_discount` and `process_order`. |