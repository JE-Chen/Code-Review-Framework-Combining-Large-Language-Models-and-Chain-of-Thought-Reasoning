Code Smell Type: Global Variable Usage  
Problem Location: `GLOBAL_RESULTS` variable defined at module level and used in `process_data` and `main`  
Detailed Explanation: The global variable creates hidden dependencies and side effects. It violates the single responsibility principle by coupling data storage with processing logic. This makes the code non-testable (requires global state) and prone to unexpected behavior during refactoring. The `process_data` function becomes impure due to its reliance on external state.  
Improvement Suggestions: Replace `GLOBAL_RESULTS` with a return value from `process_data`. Modify `main` to handle results via function return instead of global mutation. Example:  
```python  
def process_data():  
    # ... processing logic ...  
    return results_list  # Return results instead of appending to global  

def main():  
    results = process_data()  
    for r in results:  
        print("Result:", r)  
```  
Priority Level: High  

---

Code Smell Type: Duplicate Code  
Problem Location: Error handling in `get_users`, `get_posts`, and `get_comments` functions  
Detailed Explanation: Three nearly identical error handling blocks violate DRY (Don't Repeat Yourself). If error handling strategy changes (e.g., logging to file instead of `print`), all three functions must be updated. This increases maintenance cost and introduces risk of inconsistencies.  
Improvement Suggestions: Extract common request logic into a helper function:  
```python  
def _fetch(endpoint):  
    try:  
        response = requests.get(BASE_URL + endpoint, headers=HEADERS)  
        response.raise_for_status()  
        return response.json()  
    except Exception as e:  
        print(f"Error fetching {endpoint}:", e)  
        return []  

def get_users():  
    return _fetch("/users")  
```  
Priority Level: Medium  

---

Code Smell Type: Inconsistent Data Access Pattern  
Problem Location: Post processing in `process_data` (`p.get("title", "")` vs `p["title"]`)  
Detailed Explanation: The condition safely checks for `title` existence via `.get()`, but the append uses direct dictionary access (`p["title"]`). While logically safe (condition ensures key exists), this inconsistency creates confusion and risks future bugs if condition logic changes. It also violates the principle of least surprise.  
Improvement Suggestions: Use the same variable for consistency:  
```python  
title = p.get("title", "")  
if len(title) > 20:  
    GLOBAL_RESULTS.append("Long Post Title: " + title)  
```  
Priority Level: Low  

---

Code Smell Type: Missing Documentation  
Problem Location: No docstrings for functions or module-level comments  
Detailed Explanation: Absence of documentation impedes understanding of function purpose, parameters, and return values. New developers must reverse-engineer logic instead of quickly grasping intent, slowing onboarding and increasing error risk.  
Improvement Suggestions: Add docstrings:  
```python  
def get_users():  
    """Fetch user data from API. Returns list of user objects or empty list on error."""  
    # ...  
```  
Priority Level: Medium  

---

Code Smell Type: Lack of Unit Tests  
Problem Location: No test coverage for core logic  
Detailed Explanation: Critical business logic (`process_data`, API handling) lacks tests. This prevents early bug detection (e.g., the `p["title"]` access would fail if condition logic changed) and makes refactoring risky. Tests are essential for maintaining quality in production code.  
Improvement Suggestions: Implement tests for:  
1. `get_*` functions (mock HTTP responses)  
2. `process_data` (verify output against known data)  
Example using `pytest` and `unittest.mock`:  
```python  
@patch("requests.get")  
def test_get_users(mock_get):  
    mock_get.return_value.json.return_value = [{"id": 1}]  
    assert get_users() == [{"id": 1}]  
```  
Priority Level: High