### Code Quality Analysis Report

---

#### **1. Global Variable Usage**  
*Issue*:  
`GLOBAL_RESULTS` is a module-level global variable used in `process_data` and `main`, creating implicit state dependencies.  

*Root Cause*:  
The code relies on global state instead of function return values, violating encapsulation. This couples data storage with processing logic.  

*Impact*:  
- **High risk**: Makes functions non-testable (requires global setup).  
- **Maintenance cost**: Refactoring risks unintended side effects.  
- **Readability**: Hidden dependencies obscure data flow.  

*Suggested Fix*:  
Replace global mutation with explicit return values:  
```python  
def process_data():  
    # ... processing logic ...  
    return results_list  # Return results instead of global mutation  

def main():  
    results = process_data()  
    for r in results:  
        print("Result:", r)  
```  

*Best Practice*:  
**Prefer pure functions** with explicit inputs/outputs. Avoid global state to ensure modularity and testability.  

---

#### **2. Code Duplication**  
*Issue*:  
Identical HTTP request logic in `get_users`, `get_posts`, and `get_comments`.  

*Root Cause*:  
Failure to extract common logic into a reusable helper, violating DRY (Don’t Repeat Yourself).  

*Impact*:  
- **Maintenance burden**: Error handling changes require updates in 3 places.  
- **Inconsistency risk**: If one function diverges, logic becomes inconsistent.  
- **Scalability**: Adding new endpoints compounds duplication.  

*Suggested Fix*:  
Extract common logic into a helper:  
```python  
def _fetch(endpoint):  
    try:  
        response = requests.get(BASE_URL + endpoint, headers=HEADERS)  
        response.raise_for_status()  
        return response.json()  
    except Exception as e:  # Specific exception preferred (see #3)  
        print(f"Error fetching {endpoint}:", e)  
        return []  

def get_users():  
    return _fetch("/users")  
```  

*Best Practice*:  
**DRY principle**: Factor out repeated patterns into single, well-named functions.  

---

#### **3. Overly Broad Exception Handling**  
*Issue*:  
Catching `Exception` instead of specific exceptions (e.g., `requests.exceptions.RequestException`).  

*Root Cause*:  
Generic exception handling masks unexpected errors (e.g., `KeyboardInterrupt`, `SyntaxError`).  

*Impact*:  
- **Critical risk**: Hides fatal errors during development.  
- **Debugging difficulty**: Masks root causes of failures.  
- **Security**: May inadvertently suppress errors in production.  

*Suggested Fix*:  
Catch specific exceptions:  
```python  
from requests.exceptions import RequestException  

try:  
    response = requests.get(...)  
    response.raise_for_status()  
except RequestException as e:  
    print(f"API error: {e}")  
    return []  
```  

*Best Practice*:  
**Catch specific exceptions** to avoid masking unexpected failures.  

---

#### **4. Missing Documentation**  
*Issue*:  
Functions lack docstrings describing purpose, parameters, and return values.  

*Root Cause*:  
Omission of documentation during implementation.  

*Impact*:  
- **Onboarding delay**: New developers must reverse-engineer logic.  
- **Misuse risk**: Incorrect parameter usage due to unclear contracts.  
- **Knowledge loss**: Critical details become undocumented.  

*Suggested Fix*:  
Add descriptive docstrings:  
```python  
def get_users():  
    """Fetch user data from API.  
    Returns:  
        list: User objects on success, empty list on failure.  
    """  
    return _fetch("/users")  
```  

*Best Practice*:  
**Document public interfaces** using docstrings (e.g., NumPy style) for clarity.  

---

#### **5. Lack of Unit Tests**  
*Issue*:  
No tests for core logic (e.g., `process_data`, API handling).  

*Root Cause*:  
Absence of testing strategy during development.  

*Impact*:  
- **Uncaught bugs**: Edge cases (e.g., empty responses) may break silently.  
- **Refactoring fear**: Changes risk breaking functionality.  
- **Quality debt**: Critical logic lacks verification.  

*Suggested Fix*:  
Implement tests for key functions:  
```python  
# Example using pytest and unittest.mock  
@patch("requests.get")  
def test_get_users_handles_failure(mock_get):  
    mock_get.side_effect = RequestException("Timeout")  
    assert get_users() == []  
```  

*Best Practice*:  
**Test critical paths** early. Aim for 80%+ coverage on business logic.  

---

#### **6. Inconsistent Data Access Pattern**  
*Issue*:  
Mix of `.get("title", "")` (safe) and direct `p["title"]` access in `process_data`.  

*Root Cause*:  
Inconsistent coding style leading to potential bugs.  

*Impact*:  
- **Confusion**: Inconsistent access patterns confuse maintainers.  
- **Risk**: If the condition (`if len(title) > 20`) is removed later, `p["title"]` could cause `KeyError`.  

*Suggested Fix*:  
Use consistent access:  
```python  
title = p.get("title", "")  
if len(title) > 20:  
    GLOBAL_RESULTS.append("Long Post Title: " + title)  # Consistent with .get()  
```  

*Best Practice*:  
**Enforce consistency** in data access patterns (e.g., always use `.get()` for optional keys).  

---

### Summary of Severity  
| Issue                          | Severity | Priority |  
|--------------------------------|----------|----------|  
| Global Variables               | High     | Critical |  
| Code Duplication               | Medium   | High     |  
| Broad Exception Handling       | Medium   | High     |  
| Missing Documentation          | Medium   | Medium   |  
| Lack of Unit Tests             | High     | Critical |  
| Inconsistent Data Access       | Low      | Low      |  

**Key Takeaway**: Prioritize **global state removal**, **specific exception handling**, and **unit tests** to drastically improve maintainability and reliability.