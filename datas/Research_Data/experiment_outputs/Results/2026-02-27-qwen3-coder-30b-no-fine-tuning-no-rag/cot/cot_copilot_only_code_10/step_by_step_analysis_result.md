### 1. **Global Variable Usage (`no-global-variables`)**
**Issue:**  
Using a global variable `GLOBAL_CACHE` causes unintended side effects and makes testing harder because the behavior of functions depends on external mutable state.

**Root Cause:**  
The code relies on a shared global cache, which breaks encapsulation and introduces tight coupling between components.

**Impact:**  
This reduces modularity, increases risk of race conditions in concurrent environments, and hampers unit testing by making function outputs unpredictable.

**Fix Suggestion:**  
Replace the global cache with an instance-based cache inside the `APIClient` class or pass it as a parameter to avoid reliance on global scope.

```python
# Before
GLOBAL_CACHE = {}

def get_users():
    return GLOBAL_CACHE.get("users")

# After
class APIClient:
    def __init__(self, cache=None):
        self.cache = cache or {}
    
    def get_users(self):
        return self.cache.get("users")
```

**Best Practice:**  
Use dependency injection or encapsulation to manage shared state rather than relying on global variables.

---

### 2. **Unused Variable (`no-unused-vars`)**
**Issue:**  
A variable `r` is assigned but never used in the main loop — only used for printing.

**Root Cause:**  
Inefficient loop usage where intermediate variables are created unnecessarily.

**Impact:**  
Reduces code clarity and introduces minor inefficiency due to unnecessary assignment.

**Fix Suggestion:**  
Iterate directly over the list instead of assigning to an unused variable.

```python
# Before
for r in results:
    print(r)

# After
for item in results:
    print(item)
```

**Best Practice:**  
Always ensure every variable has a clear purpose. Remove unused variables to keep code clean and readable.

---

### 3. **Duplicate Code (`no-duplicate-code`)**
**Issue:**  
Functions `get_users`, `get_posts`, and `get_todos` follow almost identical logic.

**Root Cause:**  
Repetition of similar code blocks for fetching different resources from the same API.

**Impact:**  
Increases maintenance cost and makes future updates error-prone. Any change must be applied to multiple places.

**Fix Suggestion:**  
Refactor into a single generic function accepting endpoint name as a parameter.

```python
# Before
def get_users(): ...
def get_posts(): ...
def get_todos(): ...

# After
def fetch_endpoint(client, endpoint):
    # Common logic here
    pass
```

**Best Practice:**  
Apply the DRY (Don't Repeat Yourself) principle to reduce redundancy and improve maintainability.

---

### 4. **Magic Numbers/Values (`no-magic-numbers`)**
**Issue:**  
Hardcoded numeric thresholds (like 5 and 20) appear directly in conditionals.

**Root Cause:**  
These numbers have no context or meaning unless you know the domain logic behind them.

**Impact:**  
Makes the code harder to read, update, and debug. If these values change, tracking them becomes difficult.

**Fix Suggestion:**  
Extract these values into named constants.

```python
# Before
if len(results) > 20:
    ...

# After
MAX_RESULTS_THRESHOLD = 20
if len(results) > MAX_RESULTS_THRESHOLD:
    ...
```

**Best Practice:**  
Use meaningful constant names instead of magic numbers to improve readability and maintainability.

---

### 5. **Broad Exception Handling (`no-bad-exception-handling`)**
**Issue:**  
Catching `Exception` catches all possible exceptions, including unexpected ones like `KeyboardInterrupt`.

**Root Cause:**  
Overly broad exception handling masks real problems and prevents proper error propagation.

**Impact:**  
Hinders debugging and can hide serious runtime errors. Makes troubleshooting harder.

**Fix Suggestion:**  
Catch specific exceptions relevant to your use case.

```python
# Before
except Exception as e:

# After
except requests.RequestException as e:
    # Handle only expected exceptions
```

**Best Practice:**  
Always catch specific exceptions and log or re-raise unexpected ones appropriately.

---

### 6. **Side Effects in Methods (`no-unexpected-side-effects`)**
**Issue:**  
Modifying the global cache directly within the `fetch` method leads to hidden dependencies.

**Root Cause:**  
Methods modify global state, breaking encapsulation and causing unpredictable behavior.

**Impact:**  
Makes code fragile and difficult to reason about during testing or parallel execution.

**Fix Suggestion:**  
Pass the cache as an argument or encapsulate caching behavior in a dedicated service.

```python
# Before
def fetch(self, url):
    GLOBAL_CACHE[url] = data  # Modifies global

# After
def fetch(self, url, cache):
    cache[url] = data  # Explicitly managed
```

**Best Practice:**  
Avoid mutating global or external state inside methods unless absolutely necessary. Prefer passing dependencies explicitly.

---