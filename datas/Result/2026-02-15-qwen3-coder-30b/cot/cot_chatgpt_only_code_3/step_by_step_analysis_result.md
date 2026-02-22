### 1. **Unused Variable (`no-unused-vars`)**
- **Issue**: The variable `now` is defined in the function `process_order` but never used.
- **Cause**: Likely leftover from earlier development or a failed refactoring attempt.
- **Impact**: Reduces readability and may mislead readers into thinking it's intentional.
- **Fix**:
```python
def process_order(order, customer_type, now=None):
    # Remove unused 'now' parameter if not needed
    ...
```
- **Best Practice**: Always clean up unused variables during code reviews.

---

### 2. **Magic Numbers (`no-magic-numbers`) – First Instance**
- **Issue**: Hardcoded value `1000` appears directly in logic.
- **Cause**: Values without clear meaning or intent.
- **Impact**: Makes future changes harder and increases risk of errors.
- **Fix**:
```python
MIN_VIP_PURCHASE = 1000
if total >= MIN_VIP_PURCHASE:
    ...
```
- **Best Practice**: Replace magic numbers with named constants.

---

### 3. **Magic Numbers (`no-magic-numbers`) – Second Instance**
- **Issue**: Another hardcoded threshold `500`.
- **Cause**: Same root cause — lack of abstraction.
- **Impact**: Confusion and difficulty maintaining thresholds.
- **Fix**:
```python
MIN_NORMAL_PURCHASE = 500
if total >= MIN_NORMAL_PURCHASE:
    ...
```
- **Best Practice**: Group related constants under meaningful names.

---

### 4. **Magic Numbers (`no-magic-numbers`) – Third Instance**
- **Issue**: A third magic number `100`.
- **Cause**: Repetitive use of unexplained values.
- **Impact**: Reduced clarity and extensibility.
- **Fix**:
```python
MIN_DISCOUNT_THRESHOLD = 100
if total >= MIN_DISCOUNT_THRESHOLD:
    ...
```
- **Best Practice**: Prefer descriptive constants over raw literals.

---

### 5. **Duplicate Code (`no-duplicate-code`)**
- **Issue**: Similar discount logic exists in multiple branches.
- **Cause**: Lack of abstraction for shared logic.
- **Impact**: Increases maintenance burden and potential inconsistency.
- **Fix**:
```python
discount_rules = {
    "vip": lambda x: x * 0.1,
    "normal": lambda x: x * 0.05,
}
discount_func = discount_rules.get(customer_type)
if discount_func:
    discount = discount_func(total)
```
- **Best Practice**: Extract repeated patterns into reusable functions or data structures.

---

### 6. **Implicit Dependencies (`no-implicit-dependencies`)**
- **Issue**: Function modifies input dictionary directly.
- **Cause**: Direct mutation without copying.
- **Impact**: Side effects make behavior unpredictable and harder to test.
- **Fix**:
```python
def process_order(order, ...):
    order_copy = order.copy()
    order_copy['status'] = 'processed'
    return order_copy
```
- **Best Practice**: Avoid mutating inputs; prefer immutability or explicit copying.

---

### 7. **Verbose Print Statements (`no-verbose-print`) – First Instance**
- **Issue**: Use of `print()` instead of structured logging.
- **Cause**: Quick debugging instead of robust error handling.
- **Impact**: Harder to manage output in production.
- **Fix**:
```python
import logging
logging.error("Invalid order format")
```
- **Best Practice**: Replace `print()` with logging for better control and traceability.

---

### 8. **Verbose Print Statements (`no-verbose-print`) – Second Instance**
- **Issue**: Debugging output via `print()` in core logic.
- **Cause**: Mixing development aids with business logic.
- **Impact**: Makes logs noisy and less useful.
- **Fix**:
```python
logging.debug(f"Processing order {order}")
```
- **Best Practice**: Log only necessary information and keep debug logs off in production.

---

### 9. **Missing Type Hints (`no-type-checking`)**
- **Issue**: No type annotations provided.
- **Cause**: Lack of documentation or tooling support.
- **Impact**: Decreased code clarity and missed static checks.
- **Fix**:
```python
from typing import Dict, List

def create_order(items: List[tuple], total_price: float) -> Dict[str, any]:
    ...
```
- **Best Practice**: Add type hints for better IDE integration and safety.

---

### 10. **Nested Conditionals (`no-nested-conditionals`)**
- **Issue**: Deeply nested conditions reduce readability.
- **Cause**: Complex branching logic not broken down.
- **Impact**: Harder to understand and modify.
- **Fix**:
```python
if customer_type == "vip":
    if total >= 1000:
        ...
```
Could be simplified:
```python
if customer_type == "vip" and total >= 1000:
    ...
```
- **Best Practice**: Flatten complex conditionals or extract logic into helper methods.

---

### Summary of Key Fixes
| Issue | Suggested Action |
|-------|------------------|
| Unused variable | Remove or use |
| Magic numbers | Define constants |
| Duplicate code | Extract logic |
| Implicit dependencies | Copy inputs |
| Verbose prints | Switch to logging |
| Missing type hints | Add annotations |
| Nested conditionals | Simplify logic |

These improvements will enhance maintainability, testability, and readability of the codebase.