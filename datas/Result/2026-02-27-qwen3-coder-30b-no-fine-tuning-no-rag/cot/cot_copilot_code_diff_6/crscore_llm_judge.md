
    Your task is to look at a given git diff that
    represents a Python code change, linter
    feedback and code smells detected in the code
    change, and a corresponding review comment
    about the diff. You need to rate how concise,
    comprehensive, and relevant a review is and
    whether it touches upon all the important
    topics, code smells, vulnerabilities, and
    issues in the code change.
    
    Code Change:
    


    
    
    Code Smells:
    ### Code Smell Type: 
**God Function / Function That Does Too Much**

- **Problem Location:**  
  ```python
  def functionThatDoesTooMuchAndIsHardToUnderstand():
      ...
  ```

- **Detailed Explanation:**  
  The function `functionThatDoesTooMuchAndIsHardToUnderstand()` performs multiple responsibilities — making HTTP GET and POST requests, handling responses, printing status messages, and managing exceptions without clear separation of concerns. This violates the Single Responsibility Principle (SRP), making the function hard to read, debug, test, and reuse.

- **Improvement Suggestions:**  
  Split this monolithic function into smaller, focused functions:
  - One for fetching data via GET.
  - Another for posting data via POST.
  - A third to handle logging/printing results.
  - Consider adding proper error handling with specific exceptions instead of catching all exceptions.

- **Priority Level:**  
  **High**

---

### Code Smell Type: 
**Global Variables**

- **Problem Location:**  
  ```python
  GLOBAL_SESSION = requests.Session()
  ANOTHER_GLOBAL = "https://jsonplaceholder.typicode.com/posts"
  ```

- **Detailed Explanation:**  
  Using global variables makes the code harder to test, debug, and reason about because they introduce hidden dependencies. It also reduces modularity and can lead to unexpected side effects when the same variable is modified from different parts of the application.

- **Improvement Suggestions:**  
  Replace globals with parameters or inject dependencies where needed. For instance, pass `requests.Session` as an argument to functions or use dependency injection frameworks like `dependency-injector`.

- **Priority Level:**  
  **High**

---

### Code Smell Type: 
**Magic Strings / Hardcoded Values**

- **Problem Location:**  
  - `"https://jsonplaceholder.typicode.com/posts/1"`
  - `"https://jsonplaceholder.typicode.com/posts"`
  - `"https://jsonplaceholder.typicode.com/posts"`

- **Detailed Explanation:**  
  These hardcoded URLs make the code less maintainable and reusable. If the endpoint changes, you'll have to manually update every occurrence. Also, using string literals directly instead of constants reduces flexibility and readability.

- **Improvement Suggestions:**  
  Define these endpoints as named constants at the top of the module:
  ```python
  BASE_URL = "https://jsonplaceholder.typicode.com"
  POST_ENDPOINT = f"{BASE_URL}/posts"
  POST_DETAIL_ENDPOINT = f"{BASE_URL}/posts/1"
  ```

- **Priority Level:**  
  **Medium**

---

### Code Smell Type: 
**Poor Exception Handling**

- **Problem Location:**  
  ```python
  except Exception as e:
      print("錯誤但我不管:", e)

  except:
      print("第二次錯誤但我還是不管")
  ```

- **Detailed Explanation:**  
  Catching generic `Exception` or bare `except:` blocks suppresses important information and prevents proper error propagation. This makes debugging difficult and could mask real issues in production environments.

- **Improvement Suggestions:**  
  Catch more specific exceptions such as `requests.exceptions.RequestException`. Log errors appropriately using Python’s logging module rather than just printing them.

- **Priority Level:**  
  **High**

---

### Code Smell Type: 
**Inconsistent Naming Conventions**

- **Problem Location:**  
  - Function name: `functionThatDoesTooMuchAndIsHardToUnderstand()`
  - Variable names: `weirdVariableName`, `r2`

- **Detailed Explanation:**  
  The function name is not descriptive and does not convey its purpose clearly. Similarly, variable names like `weirdVariableName` and `r2` lack semantic meaning and reduce code understandability.

- **Improvement Suggestions:**  
  Rename the function to reflect what it actually does, e.g., `fetch_and_post_sample_data`. Use descriptive variable names like `response_one`, `response_two`, `post_response`.

- **Priority Level:**  
  **Medium**

---

### Code Smell Type: 
**Lack of Input Validation / Security Risk (Potential)**

- **Problem Location:**  
  The function sends raw POST data without validating or sanitizing inputs.

- **Detailed Explanation:**  
  While not directly exposed here, sending unvalidated user input via POST can open up vulnerabilities if used in a broader context. It's always good practice to validate inputs before processing.

- **Improvement Suggestions:**  
  Validate and sanitize any external inputs before using them in API calls. In this case, since it's a demo script, ensure input validation is part of the design if extended further.

- **Priority Level:**  
  **Medium**

---

### Code Smell Type: 
**No Return Values or State Management**

- **Problem Location:**  
  The function prints outputs but returns nothing, making it non-reusable and hard to integrate into larger systems.

- **Detailed Explanation:**  
  Functions that perform operations but don’t return values or manage state are hard to test and integrate into other components. They also violate principles of functional design by being purely side-effect driven.

- **Improvement Suggestions:**  
  Modify the function to return structured data (like JSON or tuples) so that calling code can process the result further. Alternatively, encapsulate behavior in classes with methods that return meaningful results.

- **Priority Level:**  
  **Medium**

---

### Code Smell Type: 
**Lack of Documentation and Comments**

- **Problem Location:**  
  No docstrings or inline comments explaining the functionality.

- **Detailed Explanation:**  
  Without documentation, even well-named functions become ambiguous. This hinders collaboration and future maintenance efforts.

- **Improvement Suggestions:**  
  Add docstrings to explain what each function does, including expected parameters and return types. Include inline comments for complex logic or unclear steps.

- **Priority Level:**  
  **Low**

---

### Summary Table:

| Code Smell Type                         | Priority |
|----------------------------------------|----------|
| God Function / Function That Does Too Much | High     |
| Global Variables                        | High     |
| Magic Strings / Hardcoded Values       | Medium   |
| Poor Exception Handling                | High     |
| Inconsistent Naming Conventions        | Medium   |
| Lack of Input Validation / Security Risk | Medium |
| Lack of Return Values or State Management | Medium |
| Lack of Documentation and Comments     | Low      |

These improvements will significantly enhance the code’s readability, maintainability, testability, and scalability.
    
    
    Linter Messages:
    ```json
[
  {
    "rule_id": "no-global-assign",
    "severity": "error",
    "message": "Assignment to global variable 'GLOBAL_SESSION' is not allowed.",
    "line": 3,
    "suggestion": "Avoid modifying global variables. Consider passing dependencies as parameters or using a class-based approach."
  },
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Unused variable 'ANOTHER_GLOBAL' declared but never used.",
    "line": 4,
    "suggestion": "Remove unused global variable 'ANOTHER_GLOBAL' if it's not needed."
  },
  {
    "rule_id": "function-name",
    "severity": "warning",
    "message": "Function name 'functionThatDoesTooMuchAndIsHardToUnderstand' is too long and doesn't clearly describe what it does.",
    "line": 6,
    "suggestion": "Rename the function to better reflect its specific responsibilities, e.g., 'fetch_and_print_post_data'."
  },
  {
    "rule_id": "no-catch-undefined",
    "severity": "error",
    "message": "Catching generic Exception without specifying type can hide unexpected errors.",
    "line": 10,
    "suggestion": "Catch specific exceptions like `requests.exceptions.RequestException` instead of bare `except:`."
  },
  {
    "rule_id": "no-catch-undefined",
    "severity": "error",
    "message": "Catching all exceptions with bare 'except:' clause prevents proper error propagation.",
    "line": 18,
    "suggestion": "Use specific exception types such as `requests.exceptions.RequestException` to handle expected failures."
  },
  {
    "rule_id": "variable-naming",
    "severity": "warning",
    "message": "Variable name 'weirdVariableName' is not descriptive enough.",
    "line": 22,
    "suggestion": "Use a more descriptive name like 'post_response' to clarify its purpose."
  },
  {
    "rule_id": "no-console",
    "severity": "warning",
    "message": "Console output (print) should not be used in production code.",
    "line": 11,
    "suggestion": "Replace print statements with logging for better control over output and debugging."
  },
  {
    "rule_id": "no-console",
    "severity": "warning",
    "message": "Console output (print) should not be used in production code.",
    "line": 12,
    "suggestion": "Replace print statements with logging for better control over output and debugging."
  },
  {
    "rule_id": "no-console",
    "severity": "warning",
    "message": "Console output (print) should not be used in production code.",
    "line": 15,
    "suggestion": "Replace print statements with logging for better control over output and debugging."
  },
  {
    "rule_id": "no-console",
    "severity": "warning",
    "message": "Console output (print) should not be used in production code.",
    "line": 16,
    "suggestion": "Replace print statements with logging for better control over output and debugging."
  },
  {
    "rule_id": "no-console",
    "severity": "warning",
    "message": "Console output (print) should not be used in production code.",
    "line": 20,
    "suggestion": "Replace print statements with logging for better control over output and debugging."
  },
  {
    "rule_id": "no-console",
    "severity": "warning",
    "message": "Console output (print) should not be used in production code.",
    "line": 23,
    "suggestion": "Replace print statements with logging for better control over output and debugging."
  }
]
```
    
    
    Review Comment:
    First code review: 

- **Readability & Consistency**:
  - Indentation is consistent, but comments are in Chinese and could be improved for international collaboration.
  - No clear formatting style (e.g., spacing around operators) — consider using a linter like `black` or `flake8`.

- **Naming Conventions**:
  - Function name `functionThatDoesTooMuchAndIsHardToUnderstand()` is too verbose and unclear; it should reflect a single responsibility.
  - Variables like `weirdVariableName` and `r2` lack descriptive meaning.
  - Global constants such as `ANOTHER_GLOBAL` should follow `UPPER_CASE` convention.

- **Software Engineering Standards**:
  - The function performs multiple responsibilities (GET, POST, logging), violating the Single Responsibility Principle.
  - Duplicate error handling logic exists for similar operations.
  - Use of global variables (`GLOBAL_SESSION`) makes code harder to test and maintain.

- **Logic & Correctness**:
  - Broad exception handling (`except:`) masks potential issues without proper logging or re-raising.
  - Lack of status code checks after POST request may lead to unexpected behavior.
  - No return values or structured output, making the function non-reusable.

- **Performance & Security**:
  - No timeout set on requests, risking hanging connections.
  - Hardcoded URLs and data reduce flexibility and introduce security risk if used in production.

- **Documentation & Testing**:
  - Missing docstrings or inline comments explaining purpose or parameters.
  - No unit tests provided; testing is needed for reliability and future changes.

- **Suggestions**:
  - Refactor into smaller functions with specific tasks.
  - Replace broad `except:` with specific exception types.
  - Add timeouts and proper error logging.
  - Rename variables and functions for clarity.
  - Move globals to a configuration module or pass as arguments.

First summary: 

## Pull Request Summary

- **Key Changes**: Introduced a new module `bad_requests.py` containing a single function that performs multiple HTTP operations (GET and POST) using a global session and hardcoded URLs.
  
- **Impact Scope**: Affects only the newly added file `bad_requests.py`. No existing modules or dependencies are impacted directly.

- **Purpose of Changes**: Likely intended as a proof-of-concept or prototype for making HTTP requests; however, it does not follow best practices and is not production-ready.

- **Risks and Considerations**:
  - The use of global variables (`GLOBAL_SESSION`, `ANOTHER_GLOBAL`) can lead to unpredictable behavior and makes testing difficult.
  - Error handling is minimal and non-specific, potentially masking issues or leading to silent failures.
  - Function name and variable names are unclear and violate readability standards.
  - Hardcoded values reduce flexibility and make future maintenance harder.

- **Items to Confirm**:
  - Whether this is an intentional prototype or part of a larger refactor.
  - If this module will be integrated into any production workflow, proper refactoring is required before merging.
  - Consider replacing global state with dependency injection for better testability and maintainability.

---

## Code Review Feedback

### 1. **Readability & Consistency**
- ❌ **Issue**: Function name `functionThatDoesTooMuchAndIsHardToUnderstand()` violates naming conventions by being too long and not descriptive.
- ⚠️ **Issue**: Mixed language (Chinese/English) in comments and output messages reduces clarity for international teams.
- ✅ **Suggestion**: Rename function to something like `fetch_and_post_data()` and standardize message language.

### 2. **Naming Conventions**
- ❌ **Issue**: Use of `weirdVariableName` and `ANOTHER_GLOBAL` is unprofessional and breaks semantic clarity.
- ✅ **Suggestion**: Rename to `post_response` and `base_url`, respectively.

### 3. **Software Engineering Standards**
- ❌ **Issue**: Single function performing multiple responsibilities (HTTP calls, logging, error handling).
- ❌ **Issue**: Global state usage (`GLOBAL_SESSION`) introduces tight coupling and makes testing difficult.
- ✅ **Suggestion**: Break down logic into smaller, reusable functions and avoid global variables.

### 4. **Logic & Correctness**
- ❌ **Issue**: Broad exception handling (`except:` without specifying types) hides potential errors.
- ❌ **Issue**: No validation of HTTP responses beyond status code checks.
- ✅ **Suggestion**: Add specific exception handling and validate response content where applicable.

### 5. **Performance & Security**
- ❌ **Issue**: Using a global `Session` object may cause issues under concurrent loads or in multi-threaded environments.
- ⚠️ **Issue**: Hardcoded URLs and credentials increase risk of exposure in version control.
- ✅ **Suggestion**: Pass session and endpoints as parameters instead of globals; externalize sensitive data.

### 6. **Documentation & Testing**
- ❌ **Issue**: Missing docstrings or inline comments explaining purpose or expected inputs/outputs.
- ❌ **Issue**: No unit or integration tests provided.
- ✅ **Suggestion**: Add basic docstrings and include unit tests for each major operation.

### 7. **Scoring & Feedback Style**
- ✅ **Overall Score**: ⚠️ Needs Improvement
- 🔍 **Feedback Style**: Concise yet comprehensive, balancing brevity with clarity. Avoids over-engineering while addressing key concerns effectively.

Total summary: 

 ### 1. **Overall Conclusion**
The PR does **not meet merge criteria** due to multiple high-priority issues that affect correctness, maintainability, and security. Key concerns include a **god function**, **global variable misuse**, **poor exception handling**, and **hardcoded values**. These issues significantly reduce code quality and increase risk of failure in production environments.

### 2. **Comprehensive Evaluation**
- **Code Quality & Correctness**:  
  The function `functionThatDoesTooMuchAndIsHardToUnderstand()` violates the Single Responsibility Principle by combining multiple operations (GET, POST, logging). Broad exception handling (`except:`) hides potential errors, and lack of structured output makes the function non-reusable.

- **Maintainability & Design Concerns**:  
  - Global variables (`GLOBAL_SESSION`, `ANOTHER_GLOBAL`) create tight coupling and hinder testing.
  - Hardcoded URLs and data reduce flexibility and introduce security risks.
  - Inconsistent naming and lack of docstrings reduce readability and collaboration.

- **Consistency with Standards**:  
  - No adherence to Python naming conventions (e.g., `weirdVariableName`).
  - Linter and code smell reports confirm inconsistent formatting and improper use of globals/exceptions.
  - No support for dependency injection or modularization.

### 3. **Final Decision Recommendation**
**Request changes**  

This PR should not be merged until core structural and design flaws are addressed. Specifically:
- Refactor the monolithic function into smaller, focused units.
- Replace global variables with injected dependencies.
- Improve exception handling and remove hardcoded values.
- Add proper documentation and logging.

### 4. **Team Follow-Up**
- Implement a modular architecture for HTTP operations (GET/POST).
- Enforce consistent naming and commenting standards.
- Integrate a linter (e.g., `flake8` or `pylint`) to enforce code style.
- Add unit tests for each logical component.
- Externalize configuration and sensitive data from code.

These actions will ensure future development aligns with team conventions and maintains long-term code health.

Step by step analysis: 

### 1. **Global Variable Assignment Not Allowed (`no-global-assign`)**
- **Issue**: You're assigning a value to `GLOBAL_SESSION`, which is a global variable.
- **Explanation**: Modifying global variables directly makes your code harder to test and reason about.
- **Root Cause**: The code assumes `GLOBAL_SESSION` exists globally and modifies it without using dependency injection or parameters.
- **Impact**: Reduces modularity, increases risk of side effects, and complicates unit testing.
- **Fix**: Avoid modifying globals; instead, pass dependencies like sessions as arguments to functions.
  ```python
  # Instead of:
  GLOBAL_SESSION = requests.Session()

  # Do:
  def fetch_data(session):
      return session.get("https://example.com")
  ```
- **Best Practice**: Prefer local scope or injected dependencies over global state.

---

### 2. **Unused Variable Detected (`no-unused-vars`)**
- **Issue**: The variable `ANOTHER_GLOBAL` is declared but never used.
- **Explanation**: Dead code clutters the program and may confuse developers.
- **Root Cause**: Either the variable was meant to be used later or was accidentally created.
- **Impact**: Decreases readability and introduces unnecessary clutter.
- **Fix**: Remove unused variables.
  ```python
  # Before:
  GLOBAL_SESSION = requests.Session()
  ANOTHER_GLOBAL = "https://jsonplaceholder.typicode.com/posts"

  # After:
  GLOBAL_SESSION = requests.Session()
  ```
- **Best Practice**: Regularly clean up unused code during refactoring.

---

### 3. **Function Name Too Long / Unclear Purpose (`function-name`)**
- **Issue**: Function name `functionThatDoesTooMuchAndIsHardToUnderstand` is too vague.
- **Explanation**: A good function name should clearly express what it does.
- **Root Cause**: Violation of Single Responsibility Principle leads to ambiguous naming.
- **Impact**: Makes code harder to understand and maintain.
- **Fix**: Rename the function to reflect one clear task.
  ```python
  # Instead of:
  def functionThatDoesTooMuchAndIsHardToUnderstand():

  # Use:
  def fetch_and_post_sample_data():
  ```
- **Best Practice**: Follow the principle that each function should do only one thing.

---

### 4. **Catching Generic Exception (`no-catch-undefined`)**
- **Issue**: Using `except:` catches all exceptions, hiding potential bugs.
- **Explanation**: It prevents proper error handling and makes debugging difficult.
- **Root Cause**: Lack of specificity in exception handling.
- **Impact**: Can mask real issues, especially in production environments.
- **Fix**: Catch specific exceptions.
  ```python
  # Instead of:
  except Exception as e:
      print("錯誤但我不管:", e)

  # Use:
  except requests.exceptions.RequestException as e:
      logger.error(f"Request failed: {e}")
  ```
- **Best Practice**: Handle known exceptions explicitly and log them appropriately.

---

### 5. **Inconsistent or Non-Descriptive Variable Names (`variable-naming`)**
- **Issue**: Variable name `weirdVariableName` lacks clarity.
- **Explanation**: Descriptive names help readers quickly grasp intent.
- **Root Cause**: Poor naming habits or lack of attention to naming standards.
- **Impact**: Reduces readability and increases cognitive load on developers.
- **Fix**: Use meaningful variable names.
  ```python
  # Instead of:
  weirdVariableName = response.text

  # Use:
  post_response = response.text
  ```
- **Best Practice**: Choose variable names that describe their purpose and content.

---

### 6. **Use of Print Statements in Production Code (`no-console`)**
- **Issue**: Multiple `print()` statements are used for outputting logs.
- **Explanation**: Print statements are not suitable for production due to limited control.
- **Root Cause**: Inadequate logging strategy.
- **Impact**: Makes deployment harder and less flexible for monitoring and debugging.
- **Fix**: Replace `print()` with Python’s `logging` module.
  ```python
  import logging
  logging.info("Data fetched successfully")
  ```
- **Best Practice**: Always use structured logging for production systems.

---

### 7. **Hardcoded URLs (`Magic Strings`)**
- **Issue**: URLs are hardcoded throughout the code.
- **Explanation**: Makes future updates harder and reduces reusability.
- **Root Cause**: Lack of abstraction for configuration values.
- **Impact**: Increases maintenance cost and error-proneness.
- **Fix**: Define constants for URLs.
  ```python
  BASE_URL = "https://jsonplaceholder.typicode.com"
  POST_ENDPOINT = f"{BASE_URL}/posts"
  POST_DETAIL_ENDPOINT = f"{BASE_URL}/posts/1"
  ```
- **Best Practice**: Extract static values into constants or config files.

---

### 8. **God Function / Function That Does Too Much**
- **Issue**: One function handles fetching, posting, printing, and error handling.
- **Explanation**: Violates the Single Responsibility Principle (SRP).
- **Root Cause**: Overloading a single function with too many tasks.
- **Impact**: Difficult to test, debug, and extend.
- **Fix**: Break it down into smaller, focused functions.
  ```python
  def fetch_post_details():
      ...

  def send_post_request():
      ...

  def log_results():
      ...
  ```
- **Best Practice**: Each function should have one clear responsibility.

---

### 9. **Lack of Input Validation (Security Risk)**
- **Issue**: No validation or sanitization of inputs.
- **Explanation**: Sending raw data without checks can lead to vulnerabilities.
- **Impact**: Potential security risks in real-world applications.
- **Fix**: Add input validation where necessary.
  ```python
  if isinstance(data, dict):
      # Proceed with safe handling
  else:
      raise ValueError("Invalid input format")
  ```
- **Best Practice**: Validate and sanitize all external inputs.

---

### 10. **No Return Values or State Management**
- **Issue**: Function has no return statement, limiting reusability.
- **Explanation**: Side-effect-only functions are hard to integrate into larger systems.
- **Impact**: Limits composability and testing capabilities.
- **Fix**: Make functions return useful data.
  ```python
  def get_post_data():
      response = session.get(url)
      return response.json()
  ```
- **Best Practice**: Functions should either return something meaningful or be designed for side effects alone.

---

### 11. **Missing Documentation and Comments**
- **Issue**: No docstrings or inline comments.
- **Explanation**: Without explanation, even good names become ambiguous.
- **Impact**: Hinders collaboration and future maintenance.
- **Fix**: Add docstrings and comments for clarity.
  ```python
  def fetch_and_post_sample_data():
      """
      Fetches a sample post and posts a new one.
      Returns:
          dict: The updated post data.
      """
  ```
- **Best Practice**: Document everything—functions, modules, and complex logic.

--- 

### Summary Table

| Issue | Description | Fix | Best Practice |
|-------|-------------|-----|----------------|
| 1 | Global assignment forbidden | Pass session as parameter | Avoid global state |
| 2 | Unused variable | Delete unused var | Clean dead code |
| 3 | Unclear function name | Rename to reflect action | SRP + descriptive naming |
| 4 | Catch-all exceptions | Catch specific exceptions | Specific error handling |
| 5 | Vague variable names | Use descriptive names | Meaningful identifiers |
| 6 | Print statements in prod | Use logging | Structured logging |
| 7 | Hardcoded URLs | Define constants | Configuration abstraction |
| 8 | God function | Split into small functions | SRP |
| 9 | Missing input validation | Add checks | Secure coding practices |
| 10 | No return values | Return structured data | Functional design |
| 11 | No docs/comments | Add docstrings/comments | Code clarity |

By addressing these points, you'll improve code quality, readability, and maintainability while reducing technical debt.
    
    
    You should first generate a step-by-step list
    of all the topics the review should cover like
    code smells, issues that would be flagged by a
    linter, security vulnerabilities, etc. Also,
    the review should cover aspects like bugs, code
    security, code readability, maintainability,
    memory consumption, performance, good and bad
    design patterns, and efficiency introduced in
    the code change. Put your analysis under a
    section titled \### Topics to be Covered:".
    
    After generating the list above you should
    again think step-by-step about the given review
    comment and whether it addresses these topics
    and put it under a section called "###
    Step-by-Step Analysis of Review Comment:". Then
    based on your step-by-step analysis you should
    generate a score ranging from 1 (minimum value)
    to 5 (maximum value) each about how
    comprehensive, concise, and relevant a review
    is. A review getting a score of 5 on
    comprehensiveness addresses nearly all the
    points in the \### Topics to be Covered:"
    section while a review scoring 1 addresses none
    of them. A review getting a score of 5 on
    conciseness only covers the topics in the \###
    Topics to be Covered:" section without wasting
    time on off-topic information while a review
    getting a score of 1 is entirely off-topic.
    Finally, a review scoring 5 on relevance is
    both concise and comprehensive while a review
    scoring 1 is neither concise nor comprehensive,
    effectively making relevance a combined score
    of conciseness and comprehensiveness. You
    should give your final rating in a section
    titled \### Final Scores:". give the final scores as shown
    below (please follow the exact format).
    
    ### Final Scores:
    ```
    ("comprehensiveness": your score, "conciseness": your score,
    "relevance": your score)
    ```
    Now start your analysis starting with the \###
    Topics to be Covered:", followed by "###
    Step-by-Step Analysis of Review Comment:" and
    ending with the \### Final Scores:".
    
    ### Topics to be Covered:
    (topics_to_be_covered)
