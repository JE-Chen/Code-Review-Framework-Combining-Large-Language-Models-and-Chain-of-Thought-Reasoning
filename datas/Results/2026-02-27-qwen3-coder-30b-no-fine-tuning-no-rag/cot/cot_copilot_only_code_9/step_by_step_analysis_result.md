### 1. **Global Variable Usage (`no-global-variables`)**
**Issue:**  
Using a global variable `GLOBAL_RESULTS` reduces modularity and testability of the code.

**Explanation:**  
A global variable makes the code harder to manage because its value can be modified from anywhere in the program. This leads to unpredictable behavior and makes it difficult to reason about the flow of data.

**Impact:**  
It complicates testing since tests cannot easily isolate or mock the global state. It also introduces side effects when the module is reused across different contexts.

**Fix Suggestion:**  
Replace the global variable with a function parameter or return value instead. For example:

```python
def process_data():
    results = []
    # ... process data ...
    return results
```

**Best Practice Tip:**  
Avoid global state. Prefer passing data as arguments and returning values rather than mutating shared state.

---

### 2. **Duplicate Code (`no-duplicate-code`)**
**Issue:**  
The `get_users()`, `get_posts()`, and `get_comments()` functions contain nearly identical logic.

**Explanation:**  
These functions all perform the same steps: send a GET request, catch exceptions, return JSON data. Copy-pasting this logic increases maintenance burden and raises the chance of inconsistencies.

**Impact:**  
If you ever need to update error handling or add retry logic, you have to do so in multiple places. This increases the risk of bugs and slows down development.

**Fix Suggestion:**  
Refactor into a single reusable function that takes an endpoint as a parameter:

```python
def fetch_data(endpoint):
    try:
        response = requests.get(f"{BASE_URL}/{endpoint}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching {endpoint}: {e}")
        return []
```

**Best Practice Tip:**  
Follow the DRY (Don’t Repeat Yourself) principle to avoid redundant code and improve maintainability.

---

### 3. **Poor Exception Handling (`no-bad-exception-handling`)**
**Issue:**  
Generic `except Exception:` catches all exceptions, hiding important details.

**Explanation:**  
This broad exception handling can mask critical errors such as network timeouts or malformed responses. You lose visibility into what went wrong.

**Impact:**  
Makes debugging harder and can cause silent failures in production systems.

**Fix Suggestion:**  
Catch specific exceptions like `requests.exceptions.RequestException`:

```python
except requests.exceptions.RequestException as e:
    print(f"Network error occurred: {e}")
```

**Best Practice Tip:**  
Always prefer catching specific exceptions over generic ones to ensure proper handling and debugging.

---

### 4. **Unhandled Errors (`no-unhandled-errors`)**
**Issue:**  
Errors are printed but not re-raised or logged properly.

**Explanation:**  
When an error occurs, simply printing it may leave calling functions unaware of the failure, leading to silent issues.

**Impact:**  
Can result in incorrect assumptions about success or failure states in the application, especially in larger workflows.

**Fix Suggestion:**  
Log the error using Python’s `logging` module and optionally re-raise it:

```python
import logging

try:
    ...
except requests.exceptions.RequestException as e:
    logging.error(f"Failed to fetch data: {e}")
    raise
```

**Best Practice Tip:**  
Proper error propagation ensures that errors don’t go unnoticed and can be handled at higher levels.

---

### 5. **Magic Numbers/Strings (`no-magic-numbers`)**
**Issue:**  
Hardcoded values like `10`, `50`, and strings like `"Special User"` reduce readability and flexibility.

**Explanation:**  
These numbers and strings are not self-documenting. Changing them requires searching throughout the codebase.

**Impact:**  
Reduced maintainability and clarity, especially when values are reused in multiple places.

**Fix Suggestion:**  
Define named constants:

```python
SPECIAL_USER_MSG = "Special User"
MAX_THRESHOLD = 50
MIN_THRESHOLD = 10
```

Then use these constants in your logic.

**Best Practice Tip:**  
Use descriptive names for magic values to make intent clear and simplify future changes.

---

### 6. **Violation of Single Responsibility Principle (SRP)**
**Issue:**  
The `process_data()` function handles fetching, filtering, and logging.

**Explanation:**  
This violates SRP, which states that a function should only do one thing. Combining responsibilities makes it harder to test and modify.

**Impact:**  
Testing becomes harder because you must simulate all behaviors at once. Changes become risky due to interdependencies.

**Fix Suggestion:**  
Split into separate functions:

```python
def fetch_and_filter(endpoint):
    raw_data = fetch_data(endpoint)
    filtered = filter_data(raw_data)
    return filtered

def display_results(results):
    # Handle output/display here
```

**Best Practice Tip:**  
Each function should focus on a single responsibility. This improves readability, testability, and scalability.

---

### 7. **Inconsistent Conditional Logic**
**Issue:**  
Nested `if` conditions in `main()` make the control flow harder to follow.

**Explanation:**  
Multiple nested conditions increase cognitive load and make the code harder to read or extend.

**Impact:**  
Increases likelihood of logic errors and makes refactoring more complex.

**Fix Suggestion:**  
Use a mapping approach or `elif` chain for clearer branching:

```python
thresholds = [(10, "Low"), (50, "Medium"), (float('inf'), "High")]

for threshold, label in thresholds:
    if count <= threshold:
        category = label
        break
```

**Best Practice Tip:**  
Simplify conditional logic by using structured approaches like dictionaries or loops for better clarity.

---

### 8. **Lack of Input Validation & Security**
**Issue:**  
No validation or sanitization of API responses.

**Explanation:**  
External APIs can return unexpected or malicious data. Without checks, the system might behave unpredictably or insecurely.

**Impact:**  
Could expose vulnerabilities to injection attacks or data corruption.

**Fix Suggestion:**  
Validate fields in responses and sanitize output before logging or displaying:

```python
if isinstance(data, dict) and 'id' in data:
    sanitized = sanitize_output(data)
```

**Best Practice Tip:**  
Treat external inputs as untrusted. Validate, sanitize, and protect against harmful data.

---

### 9. **Missing Documentation**
**Issue:**  
There are no docstrings or inline comments explaining functionality.

**Explanation:**  
Without documentation, it's hard for others to understand the code's purpose, especially complex sections like filtering logic or global usage.

**Impact:**  
Slows down onboarding of new team members and makes future modifications more error-prone.

**Fix Suggestion:**  
Add docstrings to functions:

```python
def fetch_data(endpoint):
    """
    Fetches JSON data from the specified endpoint.
    
    Args:
        endpoint (str): The API endpoint to query.

    Returns:
        list: A list of parsed JSON objects or empty list on failure.
    """
    ...
```

**Best Practice Tip:**  
Document everything: functions, classes, modules. Good docs help with understanding and maintenance.

---

### 10. **Tight Coupling Between Functions**
**Issue:**  
Functions rely on `GLOBAL_RESULTS`, making them tightly coupled.

**Explanation:**  
Dependencies on global variables make it hard to test or reuse individual components independently.

**Impact:**  
Breaks encapsulation and makes unit testing more difficult.

**Fix Suggestion:**  
Pass data explicitly via parameters instead of relying on globals:

```python
results = process_data(fetch_data("users"))
display_results(results)
```

**Best Practice Tip:**  
Minimize dependencies between modules. Explicit parameters improve modularity and testability.

---