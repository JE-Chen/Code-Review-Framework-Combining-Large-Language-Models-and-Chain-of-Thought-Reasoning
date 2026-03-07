### 1. **Unused Variable (`no-unused-vars`)**
**Issue:**  
The variable `i` in a loop is never used, indicating unnecessary code.

**Explanation:**  
This happens when a loop variable is declared but not referenced inside the loop body. It often results from copy-pasting or incomplete refactoring.

**Root Cause:**  
Developer forgot to use the loop variable or mistakenly assumed it was needed.

**Impact:**  
Low severity; affects code cleanliness and readability. May mislead readers into thinking the variable has a role.

**Fix:**  
If intentional, rename to `_` to indicate unused. Otherwise, remove or use properly.

```python
# Before
for i in range(10):
    do_something()

# After (if unused)
for _ in range(10):
    do_something()
```

**Best Practice:**  
Follow Python convention of using `_` for intentionally unused loop variables.

---

### 2. **Global Variables Without Encapsulation (`no-implicit-globals`)**
**Issue:**  
Variables `BASE_URL` and `SESSION` are defined globally without clear purpose or encapsulation.

**Explanation:**  
Using global variables makes code harder to test, debug, and maintain because their state can change unexpectedly across modules.

**Root Cause:**  
Poor architectural design — global state is tightly coupled with logic and lacks modularity.

**Impact:**  
High risk to testability, maintainability, and scalability. Makes unit testing difficult.

**Fix:**  
Encapsulate these in a class or pass them as parameters during initialization.

```python
class ApiClient:
    def __init__(self, base_url, session):
        self.base_url = base_url
        self.session = session
```

**Best Practice:**  
Avoid global state. Prefer dependency injection or encapsulation for better control over dependencies.

---

### 3. **Duplicate Case Logic (`no-duplicate-case`)**
**Issue:**  
Conditional logic duplicates behavior based on a random choice.

**Explanation:**  
Two branches in a conditional perform the same action or logic under different conditions — likely due to poor refactoring or oversight.

**Root Cause:**  
Inefficient or incorrect implementation where redundant paths exist.

**Impact:**  
Reduces code clarity and can introduce bugs if only one branch is updated later.

**Fix:**  
Simplify logic by removing duplicate behavior or make randomness explicit.

```python
# Before
if random.choice([True, False]):
    process_request()
else:
    process_request()  # Same as above!

# After
process_request()
```

**Best Practice:**  
Always ensure each branch in a conditional serves a distinct purpose.

---

### 4. **Too Broad Exception Handling (`no-unsafe-regex`)**
**Issue:**  
Catches all exceptions (`Exception`) in `parse_response`, masking real errors.

**Explanation:**  
Catching too broad an exception type hides critical runtime errors such as `TypeError`, `ValueError`, or `json.JSONDecodeError`.

**Root Cause:**  
Overly general exception handling that suppresses important diagnostic information.

**Impact:**  
Can hide serious issues like malformed data or network problems, leading to silent failures.

**Fix:**  
Catch specific exceptions instead of generic ones.

```python
# Before
except Exception as e:

# After
except json.JSONDecodeError as e:
    logger.error("JSON decoding failed", exc_info=True)
```

**Best Practice:**  
Always catch specific exceptions when possible. Log unexpected errors for debugging.

---

### 5. **Magic Number Usage (`no-magic-numbers`)**
**Issue:**  
Hardcoded value `0.05` appears in `do_network_logic`.

**Explanation:**  
A magic number is a literal value that lacks context or explanation, reducing code understanding.

**Root Cause:**  
Code was written quickly without considering future maintenance needs.

**Impact:**  
Decreases readability and makes future modifications harder.

**Fix:**  
Replace with a named constant.

```python
# Before
time.sleep(0.05)

# After
MIN_RESPONSE_TIME = 0.05
time.sleep(MIN_RESPONSE_TIME)
```

**Best Practice:**  
Extract magic numbers into meaningful constants or enums for clarity.

---

### 6. **Unnecessary Else Block (`no-unnecessary-else`)**
**Issue:**  
An `else` block follows an `if` that already returns.

**Explanation:**  
When an `if` statement ends with a return, there’s no need for an `else` clause afterward.

**Root Cause:**  
Overthinking control flow or leftover from another version of the code.

**Impact:**  
Minor readability issue but adds unnecessary nesting.

**Fix:**  
Remove the `else` block.

```python
# Before
if condition:
    return result
else:
    return fallback

# After
if condition:
    return result
return fallback
```

**Best Practice:**  
Simplify control structures to avoid redundant blocks.

---

### 7. **Catch All Exceptions (`no-catch-all`)**
**Issue:**  
Catches generic `Exception` in `main()` and suppresses important error details.

**Explanation:**  
Suppressing all exceptions makes debugging hard and can hide critical errors like system resource issues.

**Impact:**  
Very high risk — leads to silent failures and poor observability.

**Fix:**  
Catch specific exceptions or log full tracebacks.

```python
# Before
except Exception as e:
    print("Something went wrong")

# After
except requests.exceptions.RequestException as e:
    logger.error("Network error occurred", exc_info=True)
```

**Best Practice:**  
Never ignore exceptions unless absolutely necessary. When you must catch broad exceptions, log them appropriately.

---