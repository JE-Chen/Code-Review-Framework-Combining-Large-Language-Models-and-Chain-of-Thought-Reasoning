### Diff #1
**File:** `bad_requests.py`

---

### **Summary**
- **Purpose**: The code sets up a global HTTP session to make multiple requests to a public API (jsonplaceholder.typicode.com) and prints responses. It aims to demonstrate basic HTTP usage but combines unrelated operations.
- **Scope**: Entirely new file with a global session object (`GLOBAL_SESSION`), a global URL constant (`ANOTHER_GLOBAL`), and a single monolithic function (`functionThatDoesTooMuchAndIsHardToUnderstand`).
- **Plain-language explanation**: This code tries to handle multiple API requests in one messy function, uses unclear names ("weirdVariableName"), and ignores errors. It’s like writing a single grocery list for every shopping trip without separating items.

---

### **Linting Issues**
- **Global variables misuse**:  
  `GLOBAL_SESSION` and `ANOTHER_GLOBAL` are defined at module level but only used in one function. Global state complicates testing and reuse.  
  *Suggestion*: Move session creation to the function or use dependency injection.
  
- **Hardcoded URLs**:  
  `url = "https://jsonplaceholder.typicode.com/posts/1"` and `ANOTHER_GLOBAL` are hardcoded instead of being configurable.  
  *Suggestion*: Use environment variables or config objects for external endpoints.

- **Error handling gaps**:  
  `except Exception as e` and bare `except:` swallow all errors without context.  
  *Suggestion*: Handle specific exceptions (e.g., `requests.exceptions.RequestException`) and log errors.

- **Inconsistent string usage**:  
  Mixed Chinese and English strings (`"狀態碼:"`, `"錯誤但我不管:"`).  
  *Suggestion*: Use one language consistently (English preferred for code).

---

### **Code Smells**
- **Function does too much**:  
  `functionThatDoesTooMuchAndIsHardToUnderstand` combines request logic, error handling, and printing.  
  *Why bad*: Hard to test, modify, or reuse. Each request should be its own function.
  
- **Poor naming**:  
  `weirdVariableName`, `ANOTHER_GLOBAL`, and `functionThatDoesTooMuchAndIsHardToUnderstand` are unhelpful.  
  *Why bad*: Makes code opaque. Names should describe *purpose*, not *implementation*.
  
- **Global state dependency**:  
  The function relies on `GLOBAL_SESSION` and `ANOTHER_GLOBAL` without declaring it as a dependency.  
  *Why bad*: Breaks encapsulation. Testing requires global setup, and the function can’t be used elsewhere.
  
- **Silent error handling**:  
  `print("錯誤但我不管:", e)` ignores failures, hiding bugs.  
  *Why bad*: Production systems must fail safely. Errors should trigger alerts or fallbacks.
  
- **Magic numbers/strings**:  
  `"https://jsonplaceholder.typicode.com/posts/1"`, `len(r2.text)`, and `userId:1` are hardcoded.  
  *Why bad*: Changes require code edits (e.g., moving to a new endpoint). Use constants or config.