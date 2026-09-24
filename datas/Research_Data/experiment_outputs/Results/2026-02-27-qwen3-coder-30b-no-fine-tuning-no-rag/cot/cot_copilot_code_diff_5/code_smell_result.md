## Code Review Summary

### Code Smell Type: Global Variable Usage
**Problem Location:** `GLOBAL_DF` and `ANOTHER_GLOBAL` declared at module level  
**Detailed Explanation:** The use of global variables (`GLOBAL_DF`, `ANOTHER_GLOBAL`) makes the code harder to reason about, test, and maintain. Global state introduces hidden dependencies between functions and can lead to unexpected behavior when multiple parts of the application interact with these shared resources. It also reduces modularity by making functions reliant on external context rather than explicit parameters.

**Improvement Suggestions:** Replace global variables with local ones passed as arguments or returned from functions. For instance, pass the DataFrame into `functionThatDoesTooMuchAndIsNotClear()` instead of relying on a global variable. Similarly, avoid using global constants like `ANOTHER_GLOBAL` in favor of passing them explicitly where needed.

**Priority Level:** High

---

### Code Smell Type: Function Name Does Not Reflect Its Purpose
**Problem Location:** Function name `functionThatDoesTooMuchAndIsNotClear()`  
**Detailed Explanation:** This function name clearly indicates poor design — it’s vague, misleading, and violates the principle of self-documenting code. A good function name should describe what it does without needing to read its body. Using such a generic or uninformative name hinders readability and makes future maintenance more difficult.

**Improvement Suggestions:** Rename the function to something descriptive based on its actual functionality, such as `analyze_student_data()` or `generate_and_display_statistics()`. This improves clarity and helps other developers understand the purpose at a glance.

**Priority Level:** High

---

### Code Smell Type: Magic Strings
**Problem Location:** String literal `"分析開始"` used directly in code  
**Detailed Explanation:** Hardcoded strings make code less maintainable and flexible. If the string needs to be changed later, you'll have to search through the entire codebase to find every occurrence. Additionally, localization efforts become much harder if text is embedded directly in logic.

**Improvement Suggestions:** Use constants or configuration files for hardcoded strings. Define `START_MESSAGE = "分析開始"` at the top of the file and reference it throughout your code. Alternatively, consider using i18n libraries for internationalization if applicable.

**Priority Level:** Medium

---

### Code Smell Type: Violation of Single Responsibility Principle
**Problem Location:** `functionThatDoesTooMuchAndIsNotClear()`  
**Detailed Explanation:** This function performs multiple tasks: creating a dataset, modifying it, performing calculations, checking conditions, printing results, and handling exceptions. As per the SRP, each function should have only one reason to change — meaning one job. Combining too many responsibilities leads to tightly coupled, hard-to-test, and error-prone code.

**Improvement Suggestions:** Split this function into smaller, focused functions:
- One for generating the DataFrame.
- Another for adding computed columns.
- A third for calculating and displaying statistics.
- A fourth for condition checks and logging.
Each of these should take inputs and return outputs rather than manipulating globals or printing directly.

**Priority Level:** High

---

### Code Smell Type: Poor Exception Handling
**Problem Location:** `except Exception as e:` followed by `print("我不管錯誤是什麼:", e)`  
**Detailed Explanation:** Catching all exceptions (`Exception`) and silently printing them without proper logging or handling is dangerous. It hides real issues, prevents debugging, and may mask critical errors. In production systems, this kind of broad exception catching can lead to silent failures and unreliable behavior.

**Improvement Suggestions:** Be specific about which exceptions you expect and handle them appropriately. Log errors properly (using `logging` module), raise custom exceptions where appropriate, or at least provide informative feedback to users or logs. Avoid suppressing exceptions unless absolutely necessary and always log them.

**Priority Level:** High

---

### Code Smell Type: Inconsistent Indentation / Formatting
**Problem Location:** Mixed usage of tabs/spaces in code formatting  
**Detailed Explanation:** While not visible in the diff itself, inconsistent indentation can cause syntax errors in Python due to strict whitespace sensitivity. Proper formatting ensures consistency and readability across the project. Using a linter (like `flake8` or `black`) enforces standard formatting rules.

**Improvement Suggestions:** Enforce consistent indentation using a linter or formatter like Black or autopep8. Configure your editor to show whitespace characters so inconsistencies are easier to spot.

**Priority Level:** Medium

---

### Code Smell Type: Lack of Input Validation
**Problem Location:** No validation of input data before processing  
**Detailed Explanation:** There's no check whether the input DataFrame has valid structure or expected columns. If someone passes an invalid or malformed DataFrame, the code might crash or produce incorrect results. Robust applications validate their inputs early.

**Improvement Suggestions:** Add checks for required columns and data types within the function. Validate assumptions about the data shape and content before proceeding with transformations or computations.

**Priority Level:** Medium

---

### Code Smell Type: Hardcoded Random Number Generation
**Problem Location:** `random.randint(0, 10)` inside loop-like operations  
**Detailed Explanation:** Using `random.randint()` in a way that generates different values for each row introduces inconsistency and unpredictability. If reproducibility is desired, seeding the random number generator or pre-generating random values would be better approaches.

**Improvement Suggestions:** Either seed the random number generator for deterministic behavior or precompute random values outside of the loop. Also, ensure that randomness isn't being used inappropriately for statistical purposes.

**Priority Level:** Medium

---

### Code Smell Type: Lack of Unit Tests
**Problem Location:** No testing framework or unit test cases included  
**Detailed Explanation:** Without tests, there is no way to verify correctness after changes or refactorings. Even simple functions benefit greatly from unit tests, especially those involving data manipulation or conditional logic.

**Improvement Suggestions:** Introduce a testing framework like `pytest` or `unittest`. Write unit tests covering various scenarios including edge cases, normal flow, and error conditions. Test individual components independently to isolate issues quickly.

**Priority Level:** Medium

---

### Code Smell Type: Lack of Documentation
**Problem Location:** Missing docstrings or inline comments  
**Detailed Explanation:** The lack of documentation makes understanding the codebase harder for new contributors or even yourself after some time. Comments and docstrings help explain why certain decisions were made, clarify complex logic, and serve as a reference for future development.

**Improvement Suggestions:** Add docstrings to functions explaining parameters, return values, and side effects. Include inline comments for non-obvious sections of code. Follow PEP 257 for docstring conventions.

**Priority Level:** Medium

--- 

## Overall Recommendations:
To improve this code significantly:
1. Refactor large functions into smaller, focused units.
2. Eliminate reliance on global variables.
3. Improve naming conventions and add meaningful comments.
4. Implement proper error handling and logging.
5. Add unit tests and configure linting/formatters for consistency.