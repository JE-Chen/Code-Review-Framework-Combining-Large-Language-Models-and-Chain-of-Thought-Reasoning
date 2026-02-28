### 1. **Mutable Default Argument (`mutable-default-arg`)**
**Issue**:  
The default value for the `headers` parameter in a function is a dictionary, which is a mutable object. This can cause unintended side effects because the same dictionary instance is reused across function calls.

**Root Cause**:  
Python evaluates default arguments only once at function definition time. If you use a mutable default like `dict`, `list`, or `set`, changes made during one call persist in subsequent calls.

**Impact**:  
This leads to unpredictable behavior, especially in multi-threaded environments or when the function is used multiple times with the same default.

**Fix Suggestion**:  
Change the default to `None` and create a new dictionary inside the function body.

**Before**:
```python
def fetch_resource(url, headers={'Content-Type': 'application/json'}):
    ...
```

**After**:
```python
def fetch_resource(url, headers=None):
    if headers is None:
        headers = {'Content-Type': 'application/json'}
    ...
```

**Best Practice Tip**:  
Avoid using mutable objects as default values in function definitions — always initialize them inside the function.

---

### 2. **Global Variable Usage (`global-statement`)**
**Issue**:  
Inside the `fetch_resource` function, there's a reference to `fetch_resource.cache`, which modifies a global attribute. This makes the function non-deterministic and harder to test.

**Root Cause**:  
Using global state within a function introduces tight coupling and side effects, making the function rely on external state that may vary between runs or tests.

**Impact**:  
It breaks encapsulation and reduces predictability, complicating unit testing and debugging.

**Fix Suggestion**:  
Move the caching logic outside the function or pass the cache as a parameter.

**Example Fix**:
```python
def fetch_resource(url, cache=None):
    if cache is None:
        cache = {}
    # ... use cache ...
```

**Best Practice Tip**:  
Minimize reliance on global variables; prefer dependency injection or encapsulation for managing shared state.

---

### 3. **Magic Number (`magic-number`)**
**Issue**:  
A hardcoded number `1234` is used as a chunk size in `download_file`. Magic numbers reduce readability and maintainability.

**Root Cause**:  
There's no clear reasoning behind this specific value, and it's not defined as a named constant.

**Impact**:  
Future developers won’t understand why `1234` was chosen or how changing it might impact performance or memory usage.

**Fix Suggestion**:  
Define a named constant at the top of the module.

**Before**:
```python
def download_file(url, chunk_size=1234):
    ...
```

**After**:
```python
CHUNK_SIZE = 1234

def download_file(url, chunk_size=CHUNK_SIZE):
    ...
```

**Best Practice Tip**:  
Replace magic numbers with descriptive constants to improve clarity and ease of modification.

---

### 4. **Hardcoded User-Agent Strings (`hardcoded-user-agent`)**
**Issue**:  
User-Agent strings like `"iPhone"`, `"GoogleBot"`, `"Desktop"` are hardcoded directly in code, reducing flexibility and maintainability.

**Root Cause**:  
These strings are embedded directly in the source, meaning they must be manually updated if changed or extended.

**Impact**:  
Makes the code less adaptable to new requirements or configurations. Also poses potential security risks if server-side checks expect valid user agents.

**Fix Suggestion**:  
Use predefined constants or configuration settings.

**Before**:
```python
headers = {"User-Agent": "iPhone"}
```

**After**:
```python
USER_AGENTS = {
    "mobile": "iPhone",
    "bot": "GoogleBot",
    "desktop": "Desktop"
}

headers = {"User-Agent": USER_AGENTS["mobile"]}
```

**Best Practice Tip**:  
Keep sensitive or configurable values out of the codebase using constants, environment variables, or config files.

---

### 5. **Unnecessary Else Clause (`no-else-return`)**
**Issue**:  
An `else` block after a return statement is redundant and can be simplified by returning early.

**Root Cause**:  
Code unnecessarily nests logic inside an else clause, making it harder to read and follow.

**Impact**:  
Reduces readability and increases complexity for future modifications.

**Fix Suggestion**:  
Simplify conditions using early returns.

**Before**:
```python
if condition:
    return result1
else:
    return result2
```

**After**:
```python
if condition:
    return result1
return result2
```

**Best Practice Tip**:  
Prefer early returns over nested structures to keep code flat and readable.

---

### 6. **Direct Print Statements (`print-statement`)**
**Issue**:  
Using `print()` directly in business logic reduces testability and makes controlling output difficult.

**Root Cause**:  
Business logic is tightly coupled with console output, limiting flexibility in deployment or testing scenarios.

**Impact**:  
Makes unit testing harder and prevents centralized control of log/output behavior.

**Fix Suggestion**:  
Replace `print()` with logging or pass a handler function.

**Before**:
```python
def batch_fetch(urls):
    print("Starting fetch...")
    ...
```

**After**:
```python
import logging

def batch_fetch(urls, logger=logging.getLogger(__name__)):
    logger.info("Starting fetch...")
    ...
```

**Best Practice Tip**:  
Separate concerns: business logic should not dictate where logs or outputs go.

---

### 7. **Conditional Logic in Main Flow (`no-conditional-logic-in-main`)**
**Issue**:  
Business logic such as readiness checks and data fetching is mixed into the main execution flow, violating separation of concerns.

**Root Cause**:  
Main execution becomes cluttered with decision-making logic, decreasing modularity.

**Impact**:  
Harder to test, debug, and refactor. It also makes it harder to understand what happens under different conditions.

**Fix Suggestion**:  
Extract logic into dedicated helper functions.

**Before**:
```python
def main():
    if ready:
        fetch_data()
```

**After**:
```python
def main():
    check_readiness()
    process_data()

def check_readiness():
    ...

def process_data():
    ...
```

**Best Practice Tip**:  
Keep main entry points clean and delegate complex logic to smaller, focused functions.

---