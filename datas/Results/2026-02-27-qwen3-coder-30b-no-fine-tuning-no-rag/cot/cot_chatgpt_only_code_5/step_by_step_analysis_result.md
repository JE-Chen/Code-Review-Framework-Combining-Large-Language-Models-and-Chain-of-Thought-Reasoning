### 1. **Naming Convention Violation – Function Name**
- **Issue:** The function `fn_processTransactions` doesn't follow the snake_case naming convention.
- **Explanation:** In Python, function names should be lowercase with underscores (snake_case), e.g., `process_transactions`.
- **Root Cause:** The developer likely used camelCase or a prefix for clarity, but this conflicts with standard Python style.
- **Impact:** Reduces readability and consistency in a team environment.
- **Fix:** Rename the function to `process_transactions`.

```python
# Before
def fn_processTransactions(lst_transactions):
    ...

# After
def process_transactions(transactions):
    ...
```

---

### 2. **Naming Convention Violation – Variable Name**
- **Issue:** The variable `lst_transactions` violates snake_case naming.
- **Explanation:** Variables should use snake_case, so `list_transactions` or `transactions` would be better.
- **Root Cause:** Similar to function naming, it's inconsistent with PEP 8 guidelines.
- **Impact:** Makes code harder to read and maintain.
- **Fix:** Rename to `list_transactions` or `transactions`.

```python
# Before
lst_transactions = []

# After
transactions = []
```

---

### 3. **Naming Convention Violation – Class Name**
- **Issue:** Class name `TransactionStore` is already PascalCase.
- **Explanation:** Though technically correct, linter flags this because it may expect a different capitalization style or simply wants confirmation.
- **Root Cause:** Possibly due to misconfigured linter rules or false positive.
- **Impact:** Minimal impact; mostly stylistic.
- **Fix:** Leave as-is unless enforced otherwise by project policy.

---

### 4. **Generic Function Name**
- **Issue:** Function `check` lacks specificity.
- **Explanation:** A generic name doesn’t explain what condition it evaluates.
- **Root Cause:** Lazy naming, possibly due to early prototyping.
- **Impact:** Harder to understand intent without seeing implementation.
- **Fix:** Rename to something descriptive like `is_big_amount`.

```python
# Before
def check(x):
    return x > 100

# After
def is_big_amount(amount):
    return amount > BIG_TRANSACTION_THRESHOLD
```

---

### 5. **Non-descriptive Variable Name**
- **Issue:** Variable `temp` is too vague.
- **Explanation:** `temp` doesn’t indicate what it holds or why it exists.
- **Root Cause:** Temporary naming without proper documentation or context.
- **Impact:** Confuses readers unfamiliar with the scope.
- **Fix:** Use a more descriptive name such as `sorted_numbers`.

```python
# Before
temp = numbers.copy()
temp.sort()

# After
sorted_numbers = numbers.copy()
sorted_numbers.sort()
```

---

### 6. **Magic Number Usage**
- **Issue:** The number `100` appears directly in `check()`.
- **Explanation:** Hardcoded magic numbers make code less maintainable and less clear.
- **Root Cause:** Lack of abstraction for thresholds or constants.
- **Impact:** If the value needs changing, you must find every occurrence manually.
- **Fix:** Define a named constant like `MAX_AMOUNT_THRESHOLD`.

```python
# Before
if x > 100:

# After
MAX_AMOUNT_THRESHOLD = 100
if x > MAX_AMOUNT_THRESHOLD:
```

---

### 7. **Duplicate Code Block**
- **Issue:** Sorting logic repeated in `calculate_stats`.
- **Explanation:** Repeating code increases maintenance burden and risk of inconsistencies.
- **Root Cause:** No extraction into reusable helpers.
- **Impact:** Increases chance of bugs and reduces reusability.
- **Fix:** Extract sorting and statistics computation into a helper function.

```python
# Before
for n in numbers:
    temp.append(n)
temp.sort()
min_val = temp[0]
max_val = temp[-1]

# After
def compute_min_max_avg(numbers):
    return min(numbers), max(numbers), sum(numbers)/len(numbers)

min_val, max_val, avg = compute_min_max_avg(numbers)
```

---

### 8. **Global State Mutation (High Priority)**
- **Issue:** Class-level `records` list causes shared state.
- **Explanation:** Multiple instances of `TransactionStore` modify the same list.
- **Root Cause:** Mutable class attributes used instead of instance variables.
- **Impact:** Can lead to race conditions, data corruption, and test failures.
- **Fix:** Initialize `records` in `__init__`.

```python
# Before
class TransactionStore:
    records = []

# After
class TransactionStore:
    def __init__(self):
        self.records = []
```

---

### 9. **Implicit Boolean Check Inconsistency**
- **Issue:** Mixing explicit comparisons like `== 0.0` with implicit checks.
- **Explanation:** Inconsistent use of truthiness vs equality comparison can confuse logic flow.
- **Root Cause:** Not following Python idioms.
- **Impact:** Less readable and potentially buggy.
- **Fix:** Use `if not x:` for checking falsy values.

```python
# Before
if x == 0.0:

# After
if not x:
```

---

### 10. **Unreachable Code**
- **Issue:** Code after `return` in `Analyzer.analyze`.
- **Explanation:** This block will never execute, suggesting dead code or flawed control flow.
- **Root Cause:** Misplaced conditional logic or leftover debugging code.
- **Impact:** Confusing and unnecessary.
- **Fix:** Remove unreachable lines.

```python
# Before
if mode == "avg":
    return avg
else:
    return median
    # unreachable code below
    print("This won't run")

# After
if mode == "avg":
    return avg
else:
    return median
```

---

### 11. **Unnecessary `pass` Statement**
- **Issue:** Presence of `pass` where none is needed.
- **Explanation:** `pass` is often used as placeholder, but should not remain in final code.
- **Impact:** Minor stylistic issue; reduces cleanliness.
- **Fix:** Remove `pass`.

```python
# Before
if True:
    pass

# After
if True:
    pass  # Remove if not needed
```

---

### 12. **Side Effects in Function**
- **Issue:** `print_and_collect` prints to console and collects data.
- **Explanation:** Side effects make testing harder and break separation of concerns.
- **Impact:** Makes unit tests harder to write and debug.
- **Fix:** Separate logic for printing and data gathering.

```python
# Before
def print_and_collect(data):
    print(data)
    return len(data)

# After
def collect_data(data):
    return len(data)

def display_data(data):
    print(data)
```

---

### 13. **Hardcoded Date Value**
- **Issue:** Default date `'2026-01-01'` is hardcoded.
- **Explanation:** Makes future updates harder if date changes are required.
- **Impact:** Poor configurability and maintainability.
- **Fix:** Create a named constant.

```python
# Before
default_date = '2026-01-01'

# After
DEFAULT_EXPIRY_DATE = '2026-01-01'
```

--- 

### Summary of Best Practices Applied:
- **PEP 8 Compliance:** Use snake_case for functions and variables.
- **DRY Principle:** Avoid repeating logic.
- **Encapsulation & Isolation:** Avoid global state and side effects.
- **Descriptive Naming:** Choose meaningful names that clarify purpose.
- **Maintainability:** Replace magic numbers and hardcoded values with constants.