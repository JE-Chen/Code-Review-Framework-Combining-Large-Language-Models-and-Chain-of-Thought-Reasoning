
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
    
    
    Linter Messages:
    ```json
[
  {
    "rule_id": "no-global-assign",
    "severity": "error",
    "message": "Assignment to global variable 'GLOBAL_DF' detected. Global variables should be avoided to maintain modularity and testability.",
    "line": 7,
    "suggestion": "Refactor to avoid modifying global state; pass data as parameters or return values instead."
  },
  {
    "rule_id": "no-unused-vars",
    "severity": "warning",
    "message": "Unused global variable 'ANOTHER_GLOBAL' declared but never used in the code.",
    "line": 8,
    "suggestion": "Remove unused global variable 'ANOTHER_GLOBAL' if it's not needed."
  },
  {
    "rule_id": "function-max-lines",
    "severity": "error",
    "message": "Function 'functionThatDoesTooMuchAndIsNotClear' exceeds recommended maximum lines. It performs multiple unrelated tasks.",
    "line": 5,
    "suggestion": "Break down this function into smaller, focused functions that each handle one responsibility."
  },
  {
    "rule_id": "no-magic-numbers",
    "severity": "warning",
    "message": "Magic number '20' and '50' used directly in conditional logic. These should be replaced with named constants for clarity.",
    "line": 16,
    "suggestion": "Define named constants like MIN_AGE = 20 and MAX_AGE = 50 to improve readability."
  },
  {
    "rule_id": "no-bad-exception-handling",
    "severity": "error",
    "message": "Generic exception handling with broad 'except Exception as e' can mask unexpected errors and make debugging difficult.",
    "line": 19,
    "suggestion": "Catch specific exceptions or at least log the actual error type for better diagnostics."
  },
  {
    "rule_id": "no-duplicated-code",
    "severity": "warning",
    "message": "Duplicated logic for adding random scores to the DataFrame. This pattern appears twice with minor variation.",
    "line": 13,
    "suggestion": "Extract the score addition logic into a helper function to reduce duplication."
  },
  {
    "rule_id": "no-unscoped-variables",
    "severity": "error",
    "message": "Use of global keyword indicates lack of encapsulation. Global variables introduce tight coupling and side effects.",
    "line": 6,
    "suggestion": "Avoid using global variables by passing required data through parameters or returning results explicitly."
  },
  {
    "rule_id": "naming-convention",
    "severity": "warning",
    "message": "Function name 'functionThatDoesTooMuchAndIsNotClear' does not follow naming conventions and is too verbose.",
    "line": 5,
    "suggestion": "Rename function to something more descriptive and concise, such as 'analyze_age_and_scores'."
  }
]
```
    
    
    Review Comment:
    First code review: 

### Code Review Summary

- **Readability & Consistency**:  
  - Indentation and structure are consistent but could benefit from clearer separation of logic.
  - Comments are minimal; some explanation would improve understanding.

- **Naming Conventions**:  
  - Function name `functionThatDoesTooMuchAndIsNotClear()` is overly verbose and unclear.
  - Global variables `GLOBAL_DF` and `ANOTHER_GLOBAL` use inconsistent naming (UPPERCASE vs. title case), violating typical Python naming conventions.

- **Software Engineering Standards**:  
  - The function does too much (data creation, processing, printing, error handling) — violates single-responsibility principle.
  - No modularity or reusability due to heavy reliance on globals and hardcoded values.

- **Logic & Correctness**:  
  - Use of `random.randint(0, 10)` inside a loop-like operation without seeding may lead to unpredictable behavior.
  - Broad exception handling (`except Exception`) hides potential bugs and makes debugging harder.

- **Performance & Security**:  
  - No major performance or security issues, but using global state introduces risk of side effects and non-determinism.

- **Documentation & Testing**:  
  - Missing docstrings and inline comments to explain purpose and inputs.
  - No unit or integration tests provided.

---

### Suggestions for Improvement

- ✅ **Rename function**:
  - Rename `functionThatDoesTooMuchAndIsNotClear()` to something more descriptive like `analyze_and_print_data()`.
  - Break functionality into smaller helper functions for better modularity.

- ✅ **Avoid global variables**:
  - Pass data as parameters instead of relying on global scope.
  - Example: Replace `GLOBAL_DF` usage with local DataFrame input/output.

- ✅ **Improve error handling**:
  - Avoid catching generic exceptions. Catch specific ones (e.g., `TypeError`, `ValueError`) where possible.
  - Add logging or raise exceptions instead of silent printing.

- ✅ **Add documentation**:
  - Include docstrings for the main function and any complex logic.
  - Clarify what each part of the script does.

- ✅ **Refactor for clarity**:
  - Separate data generation, transformation, and output steps.
  - Consider using classes or modules to encapsulate related logic.

- ✅ **Use consistent naming**:
  - Follow PEP 8 guidelines: use `snake_case` for variables and functions, reserve `UPPER_CASE` for constants.

---

### Final Notes
This code works but lacks structure and maintainability. Refactoring it into smaller, well-defined functions with clear responsibilities will significantly improve its usability and robustness.

First summary: 

## Summary

### Key Changes
- Introduced a new module `data_analysis.py` containing a function that performs data processing and statistical analysis on a hardcoded dataset.
- The function manipulates global variables and includes basic logic for calculating average age and printing descriptive statistics.

### Impact Scope
- Affects only the newly added `data_analysis.py` file.
- Impacts any code that may import or interact with global state (`GLOBAL_DF`, `ANOTHER_GLOBAL`).

### Purpose of Changes
- Adds a simple script for demonstrating basic data manipulation and statistical output using pandas.
- Likely intended as a prototype or example for data processing workflows.

### Risks and Considerations
- **Global State Usage**: Reliance on global variables can make code harder to test, debug, and maintain.
- **Poor Function Design**: The function does too much (data creation, transformation, logic, I/O), violating single-responsibility principle.
- **Error Handling**: Generic exception handling without proper logging or recovery mechanisms.
- **Non-deterministic Behavior**: Use of `random.randint()` leads to inconsistent outputs per run.

### Items to Confirm
- Whether the use of global variables is intentional or should be refactored into local scope or classes.
- If the error handling approach is acceptable or needs improvement.
- Whether the randomness in output is desired behavior or should be made deterministic.
- Confirmation that this is a standalone example or part of a larger system requiring further modularization.

---

## Detailed Code Review

### 1. Readability & Consistency
- **Indentation & Formatting**: Indentation is consistent, but no explicit style guide mentioned (e.g., PEP8). No linter used — minor issue but could be improved.
- **Comments**: No inline comments or docstrings. Code readability suffers from lack of explanation for logic or purpose.

### 2. Naming Conventions
- **Function Name**: `functionThatDoesTooMuchAndIsNotClear()` is misleading and unhelpful. It violates naming standards by not conveying its role clearly.
- **Variables**: 
  - `GLOBAL_DF`: Suggests global variable usage, which is discouraged unless absolutely necessary.
  - `ANOTHER_GLOBAL`: Unclear what it represents or why it's a global.
- **Constants**: `ANOTHER_GLOBAL = "分析開始"` uses non-English text, which might not align with standard naming practices (especially in English-speaking teams).

### 3. Software Engineering Standards
- **Modularity**: The entire logic resides within one large function (`functionThatDoesTooMuchAndIsNotClear`) — this makes testing difficult and goes against modularity principles.
- **Duplicate/Redundant Logic**: There's no duplication here, but the same value is computed twice via `random.randint(0, 10)` for two different columns — slightly inefficient.
- **Refactoring Opportunity**: Should break up the logic into smaller functions like `create_dataframe()`, `calculate_statistics()`, etc.

### 4. Logic & Correctness
- **Control Flow Issues**: Nested `if` statements increase complexity and reduce readability.
- **Exception Handling**: Extremely generic catch-all (`except Exception as e:`) without logging or recovery — dangerous practice.
- **Boundary Conditions**: No checks for empty dataframes or invalid inputs before performing operations.
- **Determinism**: Output varies due to random number generation — makes reproduction hard.

### 5. Performance & Security
- **Performance Bottleneck**: Repeated calls to `random.randint()` inside loops (even though not explicitly looping) may affect performance in more complex scenarios.
- **Security Risk**: No user input validation, so potential for injection or misuse if extended later. However, since this is a static example, risk is low.

### 6. Documentation & Testing
- **Documentation**: Missing docstrings or inline comments explaining purpose, parameters, return values.
- **Testing**: No unit tests provided. This function cannot be easily tested in isolation due to global dependencies and side effects.

### 7. Final Score & Feedback
**Overall Score:** ⚠️ **3.5 / 5**

#### Strengths:
- Simple and straightforward implementation for demonstration purposes.

#### Areas for Improvement:
- Refactor the monolithic function into smaller, testable components.
- Replace global variables with local ones or class-based structures.
- Improve naming conventions and add meaningful comments/docs.
- Address overly broad exception handling.
- Make output deterministic where possible.

#### Suggestions:
```python
# Instead of:
def functionThatDoesTooMuchAndIsNotClear():
    ...

# Consider:
def create_sample_data():
    ...

def compute_statistics(df):
    ...

def main():
    df = create_sample_data()
    stats = compute_statistics(df)
    ...
```
This would improve testability, readability, and maintainability.

Total summary: 

 ### 1. **Overall Conclusion**
The PR does **not meet merge criteria** due to several **blocking concerns** that impact correctness, maintainability, and adherence to software engineering best practices. Key issues include:
- **Violation of core design principles**: The function `functionThatDoesTooMuchAndIsNotClear()` violates the single-responsibility principle and overuses global variables.
- **Poor error handling**: Generic exception catching without logging or recovery is a critical risk.
- **Lack of modularity and testability**: Heavy reliance on global state prevents reuse and testing.
- **Naming and documentation gaps**: Function and variable names do not conform to standard conventions, and no docstrings or comments are present.

These issues collectively prevent safe merging and require substantial refactoring before approval.

---

### 2. **Comprehensive Evaluation**

#### **Code Quality and Correctness**
- The function performs multiple unrelated tasks (data creation, modification, logic, I/O) within a single block, leading to low cohesion and high coupling.
- Use of `global` variables (`GLOBAL_DF`, `ANOTHER_GLOBAL`) introduces tight coupling and makes debugging difficult.
- Exception handling uses `except Exception` with no logging or recovery, masking potential runtime errors.
- Non-deterministic output due to repeated `random.randint()` calls reduces reliability and predictability.

#### **Maintainability and Design Concerns**
- **Code Smells Identified**:
  - Global variable usage (high priority).
  - Violation of the single-responsibility principle (high priority).
  - Poor function naming (high priority).
  - Magic strings and numbers (medium priority).
  - Absence of input validation, unit tests, and documentation (medium priority).

#### **Consistency with Existing Patterns**
- No clear alignment with standard Python naming conventions (`snake_case` for functions/variables) or architectural patterns.
- Linter and code smell reports confirm inconsistent formatting and lack of adherence to community standards.

---

### 3. **Final Decision Recommendation**
✅ **Request changes**

This PR should not be merged in its current form. The presence of:
- **Overuse of global state**, 
- **Unrefactored monolithic function**, 
- **Insecure error handling**, 
- **Poor naming and documentation practices**, 

All constitute **blocking issues** that undermine code quality and long-term maintainability.

---

### 4. **Team Follow-Up**
- Refactor `functionThatDoesTooMuchAndIsNotClear()` into smaller, focused functions.
- Remove or replace global variables with parameters or class-based structures.
- Implement specific exception handling instead of broad `except Exception`.
- Add docstrings, inline comments, and unit tests for testability.
- Enforce linting and formatting tools (e.g., `flake8`, `black`) to enforce consistency.

Step by step analysis: 

### 1. **Global Variable Assignment (`no-global-assign`)**
**Issue:**  
The code modifies a global variable `GLOBAL_DF`, which breaks modularity and makes testing difficult.

**Root Cause:**  
Using global variables introduces tight coupling between functions and creates hidden dependencies. Functions rely on external state instead of explicit parameters or return values.

**Impact:**  
This can lead to unpredictable behavior, difficulty in unit testing, and reduced maintainability. Changes to `GLOBAL_DF` in one place can unexpectedly affect other parts of the code.

**Fix Suggestion:**  
Pass data as function arguments and return results explicitly.

```python
# Before
def functionThatDoesTooMuchAndIsNotClear():
    GLOBAL_DF['score'] = random.randint(0, 10)

# After
def functionThatDoesTooMuchAndIsNotClear(df):
    df['score'] = random.randint(0, 10)
    return df
```

**Best Practice Tip:**  
Avoid global variables. Prefer encapsulation via parameters and return values.

---

### 2. **Unused Global Variable (`no-unused-vars`)**
**Issue:**  
The global variable `ANOTHER_GLOBAL` is declared but never used.

**Root Cause:**  
Unnecessary declarations clutter the namespace and indicate dead code.

**Impact:**  
It confuses readers and increases cognitive load without providing value.

**Fix Suggestion:**  
Delete unused variables.

```python
# Remove this line entirely
ANOTHER_GLOBAL = 42
```

**Best Practice Tip:**  
Keep code clean by removing unused code elements.

---

### 3. **Function Too Long (`function-max-lines`)**
**Issue:**  
Function `functionThatDoesTooMuchAndIsNotClear` does too many things and exceeds recommended length.

**Root Cause:**  
Violates the Single Responsibility Principle (SRP). The function tries to do everything — generate data, compute stats, print output, etc.

**Impact:**  
Harder to debug, test, and modify. Any small change risks breaking unrelated parts.

**Fix Suggestion:**  
Split into multiple smaller functions, each doing one task.

```python
def create_dataframe():
    # Generate initial DataFrame
    pass

def add_scores(df):
    # Add score column
    pass

def display_results(df):
    # Print summary
    pass
```

**Best Practice Tip:**  
Each function should have a single, well-defined responsibility.

---

### 4. **Magic Numbers (`no-magic-numbers`)**
**Issue:**  
Numbers like `20` and `50` appear directly in logic without explanation.

**Root Cause:**  
Hardcoded numbers reduce readability and flexibility.

**Impact:**  
If requirements change, locating all instances becomes tedious and error-prone.

**Fix Suggestion:**  
Replace with named constants.

```python
MIN_AGE = 20
MAX_AGE = 50

if age < MIN_AGE or age > MAX_AGE:
    ...
```

**Best Practice Tip:**  
Use descriptive constants instead of magic numbers.

---

### 5. **Poor Exception Handling (`no-bad-exception-handling`)**
**Issue:**  
Generic `except Exception as e:` is used, masking potential bugs.

**Root Cause:**  
Catching all exceptions prevents proper diagnosis and handling.

**Impact:**  
Silent failures and poor debugging experience in production.

**Fix Suggestion:**  
Catch specific exceptions or at least log the actual error.

```python
# Instead of:
try:
    risky_operation()
except Exception as e:
    print("I don't care what went wrong:", e)

# Do this:
try:
    risky_operation()
except ValueError as ve:
    logger.error(f"ValueError occurred: {ve}")
except KeyError as ke:
    logger.error(f"KeyError occurred: {ke}")
```

**Best Practice Tip:**  
Log or re-raise exceptions properly for better diagnostics.

---

### 6. **Duplicated Code (`no-duplicated-code`)**
**Issue:**  
Same logic for adding random scores appears twice with slight variations.

**Root Cause:**  
Code duplication increases risk of inconsistencies and makes future updates harder.

**Impact:**  
Changes must be applied in multiple places, increasing chance of bugs.

**Fix Suggestion:**  
Create a reusable helper function.

```python
def add_random_score(df):
    df['score'] = random.randint(0, 10)
    return df

# Then call it wherever needed
add_random_score(GLOBAL_DF)
```

**Best Practice Tip:**  
Follow DRY (Don’t Repeat Yourself) principle.

---

### 7. **Use of Global Keyword (`no-unscoped-variables`)**
**Issue:**  
The use of `global` keyword signals poor design and tight coupling.

**Root Cause:**  
Functions depend on global state, reducing predictability and testability.

**Impact:**  
Makes it harder to reason about code and leads to side effects.

**Fix Suggestion:**  
Avoid global state by passing inputs and returning outputs.

```python
# Instead of:
def update_global_df():
    global GLOBAL_DF
    GLOBAL_DF = ...

# Do:
def process_df(df):
    # Process df
    return updated_df
```

**Best Practice Tip:**  
Minimize global scope to enhance modularity.

---

### 8. **Unclear Function Naming (`naming-convention`)**
**Issue:**  
Function name `functionThatDoesTooMuchAndIsNotClear` is overly verbose and unclear.

**Root Cause:**  
Names should reflect purpose and be concise yet descriptive.

**Impact:**  
Confuses developers trying to understand the codebase.

**Fix Suggestion:**  
Rename to something clear and actionable.

```python
# Before
def functionThatDoesTooMuchAndIsNotClear():

# After
def analyze_age_and_scores(df):
    ...
```

**Best Practice Tip:**  
Use descriptive, short names that describe what the function does.

---
    
    
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
