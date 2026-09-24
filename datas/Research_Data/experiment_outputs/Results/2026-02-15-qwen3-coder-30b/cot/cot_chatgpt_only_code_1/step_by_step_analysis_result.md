### 1. **Global Variable Assignment (`no-global-assign`)**
- **Issue**: The code modifies a global variable `total_result`, which breaks encapsulation.
- **Why It Happens**: The function updates a shared state without clear ownership or control.
- **Impact**: Harder to test, debug, and reason about changes.
- **Fix**: Pass `total_result` as input or return it from the function.
```python
# Before
def doStuff():
    global total_result
    total_result = something

# After
def doStuff(total_result):
    return total_result + something
```
- **Best Practice**: Avoid global mutation unless absolutely required.

---

### 2. **Magic Number – π (3.14159)**
- **Issue**: Using raw numeric value for π instead of a named constant.
- **Why It Happens**: Lack of abstraction for mathematical constants.
- **Impact**: Less readable and harder to change.
- **Fix**: Define a named constant.
```python
# Before
area = radius * 3.14159

# After
PI = 3.14159
area = radius * PI
```
- **Best Practice**: Replace magic numbers with descriptive constants.

---

### 3. **Magic Number – e (2.71828)**
- **Issue**: Same problem as above for Euler's number.
- **Why It Happens**: Not treating special values as constants.
- **Impact**: Confusion during maintenance.
- **Fix**: Use named constants.
```python
# Before
exp_val = math.exp(2.71828)

# After
E = 2.71828
exp_val = math.exp(E)
```
- **Best Practice**: Prefer self-documenting values over arbitrary literals.

---

### 4. **Duplicate Key in Function Call (`no-duplicate-key`)**
- **Issue**: Passing duplicate keys to function arguments.
- **Why It Happens**: Likely due to copy-paste or unclear intent.
- **Impact**: May cause runtime errors or silent overrides.
- **Fix**: Ensure unique parameter names.
```python
# Before
doStuff(flag1=True, flag2=False, flag1=True)

# After
doStuff(flag_a=True, flag_b=False)
```
- **Best Practice**: Use meaningful, unique identifiers in function calls.

---

### 5. **Unused Variables (`no-unused-vars`)**
- **Issue**: Declared but never used variables like `temp1`, `temp2`.
- **Why It Happens**: Leftover debugging code or incomplete refactoring.
- **Impact**: Clutters logic and misleads readers.
- **Fix**: Remove unused declarations.
```python
# Before
def doStuff():
    temp1 = 10
    temp2 = 20
    return result

# After
def doStuff():
    return result
```
- **Best Practice**: Clean up dead code regularly.

---

### 6. **Implicit Boolean Check (`no-implicit-bool`)**
- **Issue**: Using `if i or j:` without explicit type awareness.
- **Why It Happens**: Relying on truthy/falsy evaluation without intent clarity.
- **Impact**: Can mask incorrect data assumptions.
- **Fix**: Be explicit with checks.
```python
# Before
if i or j:

# After
if i is not None or j is not None:
```
- **Best Practice**: Explicitly check for expected types/values.

---

### 7. **Catch-All Exception Handling (`no-implicit-any`)**
- **Issue**: Broad exception catching prevents detection of real bugs.
- **Why It Happens**: Lack of specificity in error handling.
- **Impact**: Silences legitimate failures.
- **Fix**: Handle known exceptions specifically.
```python
# Before
try:
    risky_operation()
except:
    pass

# After
try:
    risky_operation()
except ValueError as e:
    logger.error(f"Value error: {e}")
```
- **Best Practice**: Catch specific exceptions and log accordingly.

---

### 8. **Mutable Default Argument (`no-unsafe-default-arg`)**
- **Issue**: Mutable default argument causes unintended shared state.
- **Why It Happens**: Common Python gotcha when defaulting to mutable objects.
- **Impact**: Side effects across function calls.
- **Fix**: Initialize inside function body.
```python
# Before
def collectValues(x, bucket=[]):

# After
def collectValues(x, bucket=None):
    bucket = bucket or []
```
- **Best Practice**: Never use mutable defaults like `[]` or `{}`.

---

### 9. **Deeply Nested Conditionals (`no-nested-conditionals`)**
- **Issue**: Complex control flow reduces readability.
- **Why It Happens**: Lack of early returns or helper functions.
- **Impact**: Increases chance of logic bugs.
- **Fix**: Flatten structure with guards or extract logic.
```python
# Before
if cond1:
    if cond2:
        if cond3:
            do_something()

# After
if not cond1:
    return
if not cond2:
    return
if not cond3:
    return
do_something()
```
- **Best Practice**: Refactor nested structures into cleaner control flows.

---

### 10. **Unnecessary Side Effects in Loop (`no-side-effects-in-loop`)**
- **Issue**: Artificial delay slows down execution unnecessarily.
- **Why It Happens**: Misplaced timing logic or debugging artifacts.
- **Impact**: Performance degradation.
- **Fix**: Move delays outside loops.
```python
# Before
for item in items:
    time.sleep(0.01)
    process(item)

# After
for item in items:
    process(item)
time.sleep(0.01)
```
- **Best Practice**: Avoid side effects inside tight loops.

---

### 11. **Duplicated Code (`no-duplicated-code`)**
- **Issue**: Repetitive patterns suggest missing abstraction.
- **Why It Happens**: Lack of modularization or reuse strategies.
- **Impact**: Difficult to update and maintain.
- **Fix**: Extract logic into reusable helpers.
```python
# Before
if x > 0:
    result = x * 2
else:
    result = x * 3

if y > 0:
    result2 = y * 2
else:
    result2 = y * 3

# After
def scale(val):
    return val * 2 if val > 0 else val * 3
result = scale(x)
result2 = scale(y)
```
- **Best Practice**: Apply DRY (Don’t Repeat Yourself) principles.

--- 

### 12. **Poor Naming (`Naming Convention Violation`)**
- **Issue**: Generic or misleading names such as `doStuff`, `sum`, `r`.
- **Why It Happens**: Lack of focus on clarity and semantics.
- **Impact**: Makes code harder to understand.
- **Fix**: Choose descriptive names.
```python
# Before
def doStuff(): ...

# After
def calculateArea(): ...
```
- **Best Practice**: Choose expressive and consistent names.

---

### 13. **Inconsistent Return Types**
- **Issue**: Casting floats to strings then back to float.
- **Why It Happens**: Overcomplicated conversion logic.
- **Impact**: Minor inefficiency and confusion.
- **Fix**: Return appropriate types directly.
```python
# Before
return str(float(total))

# After
return float(total)
```
- **Best Practice**: Match return types to expected outputs.

---

### 14. **Too Many Boolean Flags**
- **Issue**: Function signature overloaded with flags.
- **Why It Happens**: Lack of structure or abstraction.
- **Impact**: Reduced usability and readability.
- **Fix**: Group flags into options or enums.
```python
# Before
doStuff(flag1=True, flag2=False, flag3=True)

# After
config = {"enable_logging": True, "use_cache": False}
doStuff(config)
```
- **Best Practice**: Prefer structured inputs over boolean switches.

---

### 15. **Missing Documentation**
- **Issue**: No docstrings or comments.
- **Why It Happens**: Oversight or lack of documentation habits.
- **Impact**: Slows adoption and maintenance.
- **Fix**: Add docstrings.
```python
def processEverything(data):
    """Process input data and return transformed value."""
    ...
```
- **Best Practice**: Document interfaces and behaviors clearly.

---

### 16. **Implicit Truthiness Usage**
- **Issue**: Reliance on implicit boolean behavior.
- **Why It Happens**: Lazy assumptions around falsy/truthy.
- **Impact**: Subtle bugs in edge cases.
- **Fix**: Be precise with comparisons.
```python
# Before
if a % 2 == 0:

# After
if isinstance(a, int) and a % 2 == 0:
```
- **Best Practice**: Avoid implicit assumptions about value types.

---

### Final Recommendations Summary:
| Category                 | Action Taken |
|--------------------------|--------------|
| Encapsulation            | Avoid globals |
| Constants                | Use named values |
| Readability              | Flatten conditionals |
| Testing                  | Eliminate side effects |
| Maintainability          | Reduce duplication |
| Safety                   | Specific exception handling |
| Design                   | Modularize functions |
| Naming                   | Improve variable/function names |
| Clarity                  | Add docs/comments |

By addressing these points systematically, the overall code quality improves significantly, making it safer, faster, and easier to extend.