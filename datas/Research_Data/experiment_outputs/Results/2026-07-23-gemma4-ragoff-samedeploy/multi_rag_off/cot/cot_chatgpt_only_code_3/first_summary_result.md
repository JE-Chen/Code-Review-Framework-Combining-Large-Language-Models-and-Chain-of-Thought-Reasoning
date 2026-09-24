This code review is conducted based on the provided global rules.

### 1. Readability & Consistency
- **Formatting:** The code is generally well-formatted and follows standard Python indentation.
- **Consistency:** The use of `print` statements for both business logic errors (e.g., "No items") and debugging (`verbose=True`) is inconsistent. Business logic errors should ideally be handled via exceptions or a dedicated logging system.

### 2. Naming Conventions
- **Descriptive Names:** Variable and function names (e.g., `calculate_discount`, `process_order`) are clear and descriptive.
- **Semantic Clarity:** The naming is consistent across the codebase.

### 3. Software Engineering Standards
- **Modularity:** The logic is split into functions, but there is a lack of data encapsulation. Using a `dict` for an `Order` makes the code fragile; a `dataclass` or `NamedTuple` would provide better structure and type safety.
- **Abstraction (Liskov Substitution Principle):** The `log_order` function uses `hasattr` to check for `log` or `write` methods. This is a "code smell." The `FileLogger` and `ConsoleLogger` should implement a common interface (Abstract Base Class) so that `log_order` can call a single method regardless of the logger implementation.
- **Redundancy:** In `process_order`, `order["paid"] = False` is set both in `create_order` and again in `process_order`, which is redundant.

### 4. Logic & Correctness
- **Input Validation:** `process_order` checks if `"items"` exists and if the list is empty, but it does not validate if the items are actually tuples of `(name, price)`. A malformed item would cause a `TypeError` or `IndexError`.
- **Boundary Conditions:** The discount logic in `calculate_discount` correctly handles the thresholds (1000, 500), but the `else: discount = 0` for `normal` customers is redundant as `discount` is initialized to 0.

### 5. Performance & Security
- **Performance:** No significant bottlenecks identified for the current scale.
- **Security:** No external inputs are processed, so there are no immediate injection risks. However, the use of `print` for logging is not suitable for production environments.

### 6. Documentation & Testing
- **Documentation:** The code lacks docstrings for functions and classes. It is unclear what the expected types for `items` or `created_at` are without reading the implementation.
- **Testing:** No unit tests are provided. The `main()` function serves as a manual smoke test, but automated tests are needed to verify the discount logic and order processing.

---

### Summary of Recommendations

| Category | Issue | Recommendation |
| :--- | :--- | :--- |
| **Architecture** | Use of `dict` for Order | Replace `order = {}` with a `@dataclass` for type safety. |
| **Architecture** | Logger Interface | Create a `Logger` base class with a `log()` method to remove `hasattr` checks. |
| **Correctness** | Error Handling | Replace `print("No items")` with a custom exception (e.g., `EmptyOrderError`). |
| **Documentation** | Missing Docstrings | Add PEP 257 compliant docstrings to all public functions and classes. |
| **Testing** | No Unit Tests | Implement tests for `calculate_discount` covering all customer types and price brackets. |