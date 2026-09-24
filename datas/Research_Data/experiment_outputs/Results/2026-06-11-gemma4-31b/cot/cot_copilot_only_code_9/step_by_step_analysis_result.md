I have analyzed the provided Linter Results and Code Smell Report. Below is the step-by-step breakdown of the issues and their resolutions.

---

### 1. Duplicated Code / Lack of Abstraction
**Identify the Issue:** The functions `get_users`, `get_posts`, and `get_comments` share identical logic.  
**Root Cause Analysis:** This occurs when a developer writes separate functions for similar tasks instead of creating a parameterized helper. It is a violation of the **DRY (Don't Repeat Yourself)** principle.  
**Impact Assessment:** **High Severity.** Maintenance becomes difficult; changing the timeout or header logic requires updates in three different places, increasing the chance of bugs.  
**Suggested Fix:** Implement a single `fetch_resource(endpoint)` function that accepts the endpoint as an argument.  
**Best Practice Note:** Use **Abstraction**. Generalize repetitive patterns into a single reusable component to ensure consistency.

---

### 2. Use of Global State (`GLOBAL_RESULTS`)
**Identify the Issue:** Data is stored and modified in a global variable across different functions.  
**Root Cause Analysis:** This is a shortcut to avoid passing arguments between functions, resulting in "impure" functions that depend on external state.  
**Impact Assessment:** **High Severity.** This ruins testability (tests cannot be run in isolation), prevents thread safety, and makes debugging difficult as any function can change the data.  
**Suggested Fix:** Return the processed data from the function and pass it as a parameter to the next.  
**Best Practice Note:** Prefer **Functional Purity**. Functions should take inputs and return outputs without modifying the environment outside their scope.

---

### 3. Broad Exception Handling (`except Exception`)
**Identify the Issue:** The code catches all possible errors using a generic `Exception` block.  
**Root Cause Analysis:** The developer likely wanted to prevent the app from crashing but did not specify which errors were expected.  
**Impact Assessment:** **Medium Severity.** This masks critical system errors (like `KeyboardInterrupt` or `MemoryError`), making the application behave unpredictably and hiding the true cause of failures.  
**Suggested Fix:** Catch specific exceptions, such as `requests.exceptions.RequestException`.  
**Best Practice Note:** Follow the **Principle of Least Privilege** in error handling—only catch the exceptions you know how to handle.

---

### 4. Unhandled HTTP Status & Missing Timeouts
**Identify the Issue:** The code calls `.json()` immediately after a request without verifying the response code or setting a timeout.  
**Root Cause Analysis:** Over-reliance on the "happy path" (assuming the server always returns 200 OK and responds quickly).  
**Impact Assessment:** **High Severity.** If the API returns a 500 error, `.json()` may fail or process garbage data. Without a timeout, the application could hang indefinitely (Zombie process) if the server is unresponsive.  
**Suggested Fix:** Add `response.raise_for_status()` and `timeout=10` to the `requests.get()` call.  
**Best Practice Note:** Always assume external network calls will fail. Implement **Defensive Programming**.

---

### 5. Unclear Naming & Potential KeyErrors
**Identify the Issue:** Use of single-letter variables (`u`, `p`, `c`) and direct dictionary access (`p["title"]`).  
**Root Cause Analysis:** This is often a result of "scripting mindset" where speed of typing is prioritized over readability and safety.  
**Impact Assessment:** **Low to Medium Severity.** Poor naming increases cognitive load for other developers. Direct key access causes the program to crash with a `KeyError` if the API schema changes.  
**Suggested Fix:** Use descriptive names (`user`, `post`) and the `.get()` method for dictionary access.  
**Best Practice Note:** Prioritize **Readability over Brevity**. Code is read far more often than it is written.

---

### 6. Deeply Nested Logic (Arrow Anti-pattern)
**Identify the Issue:** The `main()` function uses nested `if-else` blocks for result counting.  
**Root Cause Analysis:** A failure to use linear conditional logic (`elif`), creating a "staircase" of indentation.  
**Impact Assessment:** **Low Severity.** It primarily affects readability and makes the logic flow harder to trace.  
**Suggested Fix:** Flatten the structure using an `if-elif-else` chain.  
**Best Practice Note:** Aim for **Flat Code**. Reduce nesting to lower the cognitive complexity of the logic.