
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
    ### Code Smell Type: Global Variables
- **Problem Location:** `GLOBAL_THING`, `STRANGE_CACHE`
- **Detailed Explanation:** The use of global variables (`GLOBAL_THING` and `STRANGE_CACHE`) introduces hidden coupling between different parts of the code. This makes it difficult to reason about the behavior of the code and test its components independently. Global variables can lead to unexpected side effects and make the code harder to understand and maintain.
- **Improvement Suggestions:** Pass these values as parameters to functions or encapsulate them within a dedicated object to limit their scope and impact.
- **Priority Level:** High

### Code Smell Type: Magic Numbers
- **Problem Location:** `MAGIC = 37`
- **Detailed Explanation:** Magic numbers (numbers without context) make the code harder to read and understand. They should be defined as named constants to provide clarity.
- **Improvement Suggestions:** Replace `MAGIC` with a named constant like `MATH_CONSTANT`.
- **Priority Level:** Medium

### Code Smell Type: Long Function
- **Problem Location:** `do_everything_and_nothing_at_once`
- **Detailed Explanation:** The function `do_everything_and_nothing_at_once` is overly complex and does too many things. It handles data generation, processing, analysis, and visualization.
- **Improvement Suggestions:** Break down the function into smaller, more focused functions each responsible for a single task.
- **Priority Level:** High

### Code Smell Type: Unnecessary Computation
- **Problem Location:** Inside the loop where `value` is calculated and processed.
- **Detailed Explanation:** Some computations (like converting `value` to float) are performed repeatedly and unnecessarily.
- **Improvement Suggestions:** Cache results of expensive computations and avoid redundant type conversions.
- **Priority Level:** Medium

### Code Smell Type: Inefficient Use of Exceptions
- **Problem Location:** Multiple uses of `try-except` blocks for error handling.
- **Detailed Explanation:** Using exceptions for control flow is generally discouraged. It can hide bugs and make the code harder to understand.
- **Improvement Suggestions:** Replace `try-except` with conditional checks where possible.
- **Priority Level:** Medium

### Code Smell Type: Hardcoded Constants
- **Problem Location:** Hardcoding constants like the number of samples in the loop.
- **Detailed Explanation:** Hardcoded constants make the code less flexible and harder to change.
- **Improvement Suggestions:** Encapsulate these constants within a configuration object or use environment variables.
- **Priority Level:** Low

### Code Smell Type: Unnecessary Loop
- **Problem Location:** The final loop that prints the flag values.
- **Detailed Explanation:** This loop adds no value to the function's purpose and can be removed.
- **Improvement Suggestions:** Remove the unnecessary loop.
- **Priority Level:** Low

### Code Smell Type: Overuse of List Comprehensions
- **Problem Location:** The list comprehension used to create `df["col_two"]`.
- **Detailed Explanation:** While list comprehensions are often preferred for readability, they can sometimes be overused and lead to performance issues.
- **Improvement Suggestions:** Consider using explicit loops for better readability and performance.
- **Priority Level:** Medium

### Code Smell Type: Potential Division by Zero
- **Problem Location:** Calculation of `weird_sum` and division in `df["normalized"]`.
- **Detailed Explanation:** There is a risk of division by zero if `weird_sum` is zero.
- **Improvement Suggestions:** Add a check to handle the case where `weird_sum` is zero.
- **Priority Level:** Medium

### Code Smell Type: Implicit Return Types
- **Problem Location:** The function returns a tuple containing a DataFrame and a dictionary.
- **Detailed Explanation:** Functions should ideally have a single, consistent return type.
- **Improvement Suggestions:** Define a custom result class or namedtuple to return multiple values.
- **Priority Level:** Medium

### Code Smell Type: Inconsistent Handling of Input Parameters
- **Problem Location:** The function accepts default values for parameters.
- **Detailed Explanation:** Default parameter values can lead to unexpected behavior if the function is called multiple times.
- **Improvement Suggestions:** Avoid using mutable default values or reinitialize them within the function.
- **Priority Level:** Medium

### Code Smell Type: Lack of Comments
- **Problem Location:** Various parts of the code lack explanatory comments.
- **Detailed Explanation:** Lack of comments makes the code harder to understand and maintain.
- **Improvement Suggestions:** Add comments to explain complex logic or non-obvious decisions.
- **Priority Level:** Low

### Code Smell Type: Redundant Operations
- **Problem Location:** Calculation of `weird_sum` and its use in normalization.
- **Detailed Explanation:** The calculation of `weird_sum` is repeated and could be cached.
- **Improvement Suggestions:** Cache the result of `weird_sum` to avoid redundant computation.
- **Priority Level:** Medium

### Code Smell Type: Use of `time.sleep`
- **Problem Location:** The use of `time.sleep` for arbitrary delays.
- **Detailed Explanation:** Arbitrary delays can make the code harder to test and reason about.
- **Improvement Suggestions:** Replace delays with proper timing mechanisms or configurable sleep durations.
- **Priority Level:** Medium

### Code Smell Type: Overuse of `plt.show()`
- **Problem Location:** The call to `plt.show()` at the end of the function.
- **Detailed Explanation:** Calling `plt.show()` directly in the function can interfere with other plots or scripts.
- **Improvement Suggestions:** Encapsulate plotting logic within a separate function or module.
- **Priority Level:** Medium

By addressing these code smells, the code will become more readable, maintainable, and easier to test.
    
    
    Linter Messages:
    ```json
[
    {
        "rule_id": "global-variables",
        "severity": "error",
        "message": "Using global variables can lead to unexpected behavior and difficulties in testing.",
        "line": 9,
        "suggestion": "Pass global variables as parameters to functions."
    },
    {
        "rule_id": "mutable-default-arguments",
        "severity": "error",
        "message": "Mutable default arguments like lists and dictionaries can lead to unexpected behavior.",
        "line": 14,
        "suggestion": "Initialize mutable defaults within the function body."
    },
    {
        "rule_id": "unhandled-exceptions",
        "severity": "error",
        "message": "Exception handling without specific exceptions can hide bugs.",
        "line": 23,
        "suggestion": "Catch specific exceptions or re-raise them with context."
    },
    {
        "rule_id": "unnecessary-complexity",
        "severity": "warning",
        "message": "The function does too many things and lacks clarity.",
        "line": 13,
        "suggestion": "Split the function into smaller, more focused functions."
    },
    {
        "rule_id": "inefficient-calculation",
        "severity": "warning",
        "message": "Repeating calculations inside loops can impact performance.",
        "line": 26,
        "suggestion": "Cache results of expensive calculations."
    },
    {
        "rule_id": "redundant-code",
        "severity": "warning",
        "message": "The same code appears multiple times.",
        "line": 36,
        "suggestion": "Refactor out repeated logic into a separate function."
    },
    {
        "rule_id": "inconsistent-return-types",
        "severity": "error",
        "message": "The function returns different types based on conditions.",
        "line": 47,
        "suggestion": "Ensure consistent return types."
    },
    {
        "rule_id": "unnecessary-imports",
        "severity": "info",
        "message": "Some imports are not used in the code.",
        "line": 4,
        "suggestion": "Remove unused imports."
    }
]
```
    
    
    Review Comment:
    First code review: 

### Code Review Template

## Review Rules
1. **Code Readability**:
   - Ensure proper indentation, consistent formatting, and clear comments.
   
2. **Clarity and Descriptive Names**:
   - Variable, function, and class names should be descriptive and meaningful.
   
3. **Software Engineering Standards**:
   - Code should be modular, maintainable, and testable.
   - Avoid global variables and shared mutable states.
   
4. **Logic & Correctness**:
   - Verify correctness of program logic and identify potential bugs.
   
5. **Performance & Security**:
   - Assess for unnecessary performance bottlenecks.
   - Review for security risks (e.g., input validation, resource management).
   
6. **Documentation & Testing**:
   - Ensure necessary comments and documentation are present.
   - Verify sufficient unit and integration tests are included.
   
7. **Scoring & Feedback Style**:
   - Balance conciseness with comprehensiveness.
   - Do not penalize completeness for being less concise.

## Code Diff

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import math
import sys
import time

GLOBAL_THING = None
STRANGE_CACHE = {}
MAGIC = 37

def do_everything_and_nothing_at_once(x=None, y=[], z={"a": 1}):
    global GLOBAL_THING

    if x is None:
        x = random.randint(10, 200)

    data_container = []
    counter = 0

    while counter < x:
        if counter % 2 == 0:
            value = counter * random.random()
        else:
            value = math.sqrt(counter + MAGIC) if counter + MAGIC > 0 else 0

        if counter % 5 == 0:
            try:
                value = float(str(value))
            except:
                pass

        data_container.append(value)
        counter += 1

    GLOBAL_THING = data_container

    df = pd.DataFrame({
        "col_one": data_container,
        "col_two": [random.randint(1, 100) for _ in range(len(data_container))],
        "col_three": np.random.randn(len(data_container))
    })

    df["mystery"] = df.apply(
        lambda row: (row["col_one"] * 1.5 + row["col_two"])
        if row["col_two"] % 3 != 0
        else row["col_three"] * MAGIC,
        axis=1
    )

    weird_sum = 0
    for i in range(len(df)):
        try:
            if df.iloc[i]["mystery"] > 0:
                weird_sum += df.iloc[i]["mystery"]
            else:
                weird_sum += abs(df.iloc[i]["col_three"])
        except Exception as e:
            weird_sum += 0

    df["normalized"] = df["mystery"].apply(
        lambda x: x / weird_sum if weird_sum != 0 else 0
    )

    temp = None
    for k in range(3):
        temp = df.sample(frac=0.5 if k % 2 == 0 else 0.3)
        STRANGE_CACHE[k] = temp.describe()

    result = {
        "mean": df["mystery"].mean(),
        "std": df["mystery"].std(),
        "max": max(df["mystery"]),
        "min": min(df["mystery"]),
        "something_useless": sum([i for i in range(10)])
    }

    try:
        if result["mean"] > result["std"]:
            df["flag"] = df["normalized"].apply(lambda v: 1 if v > 0.01 else 0)
        else:
            df["flag"] = df["normalized"].apply(lambda v: -1 if v < 0 else 0)
    except:
        df["flag"] = 0

    for _ in range(2):
        time.sleep(0.01)

    plt.figure()
    plt.plot(df["col_one"], label="col_one maybe")
    plt.plot(df["mystery"], label="mystery stuff")
    plt.legend()
    plt.title("Definitely a Meaningful Analysis")
    plt.xlabel("Index-ish")
    plt.ylabel("Values-ish")
    plt.tight_layout()
    plt.show()

    return df, result


if __name__ == "__main__":
    output_df, summary = do_everything_and_nothing_at_once()

    print("=== Summary That Probably Matters ===")
    for k in summary:
        print(k, "=>", summary[k])

    if GLOBAL_THING is not None and len(GLOBAL_THING) > 0:
        print("First thing:", GLOBAL_THING[0])
    else:
        print("Nothing happened, but also something did.")
```

### Feedback

- **Readability & Consistency**:
  - **Indentation**: The code uses a mix of tabs and spaces. Ensure consistent use of either tabs or spaces.
  - **Comments**: Add comments to explain complex sections of the code.
  
- **Naming Conventions**:
  - `GLOBAL_THING`, `STRANGE_CACHE`, and `MAGIC` are not descriptive. Rename them to more meaningful names like `global_data`, `cache_results`, and `magic_number`.
  
- **Software Engineering Standards**:
  - Global variables (`GLOBAL_THING`, `STRANGE_CACHE`) should be avoided. Pass data through function parameters or use classes.
  - The function `do_everything_and_nothing_at_once` does too much. Break it down into smaller functions with a single responsibility.
  
- **Logic & Correctness**:
  - The exception handling around `float(str(value))` and `df.iloc[i]["mystery"]` is overly broad. Catch specific exceptions.
  
- **Performance & Security**:
  - The loop inside the plot call might cause performance issues for large datasets. Consider optimizing or breaking it into smaller chunks.
  
- **Documentation & Testing**:
  - Add docstrings to functions explaining their purpose and parameters.
  - Include unit tests for key functionalities.

### Improvement Suggestions

1. **Refactor Functions**:
   - Split `do_everything_and_nothing_at_once` into smaller functions like `generate_data`, `process_data`, `analyze_data`, etc.

2. **Avoid Global Variables**:
   - Use local variables within functions or encapsulate them in classes.

3. **Optimize Loops**:
   - Avoid unnecessary loops and expensive operations inside critical paths.

4. **Exception Handling**:
   - Be specific about exceptions caught and handle them appropriately.

5. **Add Documentation**:
   - Document each function with docstrings explaining its purpose and parameters.

First summary: 

### PR Summary Template

#### Summary Rules
- **Key changes**: The code introduces a function `do_everything_and_nothing_at_once` which generates a DataFrame, applies various transformations, and plots the results. It uses global variables and caches intermediate results.
- **Impact scope**: This affects the entire script, including data generation, processing, and visualization.
- **Purpose of changes**: To add a comprehensive example demonstrating data manipulation, transformation, and plotting.
- **Risks and considerations**: Global variables (`GLOBAL_THING`, `STRANGE_CACHE`) may lead to unexpected side effects. Potential performance issues due to repetitive operations.
- **Items to confirm**:
  - Validate the logic of each step.
  - Ensure proper exception handling.
  - Confirm the use of global variables is intentional and justified.
- **Avoid excessive technical detail**: Keep the summary high-level for quick team understanding.

### Code Diff to Review

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import math
import sys
import time

GLOBAL_THING = None
STRANGE_CACHE = {}
MAGIC = 37


def do_everything_and_nothing_at_once(x=None, y=[], z={"a": 1}):
    global GLOBAL_THING

    if x is None:
        x = random.randint(10, 200)

    data_container = []
    counter = 0

    while counter < x:
        if counter % 2 == 0:
            value = counter * random.random()
        else:
            value = math.sqrt(counter + MAGIC) if counter + MAGIC > 0 else 0

        if counter % 5 == 0:
            try:
                value = float(str(value))
            except:
                pass

        data_container.append(value)
        counter += 1

    GLOBAL_THING = data_container

    df = pd.DataFrame({
        "col_one": data_container,
        "col_two": [random.randint(1, 100) for _ in range(len(data_container))],
        "col_three": np.random.randn(len(data_container))
    })

    df["mystery"] = df.apply(
        lambda row: (row["col_one"] * 1.5 + row["col_two"])
        if row["col_two"] % 3 != 0
        else row["col_three"] * MAGIC,
        axis=1
    )

    weird_sum = 0
    for i in range(len(df)):
        try:
            if df.iloc[i]["mystery"] > 0:
                weird_sum += df.iloc[i]["mystery"]
            else:
                weird_sum += abs(df.iloc[i]["col_three"])
        except Exception as e:
            weird_sum += 0

    df["normalized"] = df["mystery"].apply(
        lambda x: x / weird_sum if weird_sum != 0 else 0
    )

    temp = None
    for k in range(3):
        temp = df.sample(frac=0.5 if k % 2 == 0 else 0.3)
        STRANGE_CACHE[k] = temp.describe()

    result = {
        "mean": df["mystery"].mean(),
        "std": df["mystery"].std(),
        "max": max(df["mystery"]),
        "min": min(df["mystery"]),
        "something_useless": sum([i for i in range(10)])
    }

    try:
        if result["mean"] > result["std"]:
            df["flag"] = df["normalized"].apply(lambda v: 1 if v > 0.01 else 0)
        else:
            df["flag"] = df["normalized"].apply(lambda v: -1 if v < 0 else 0)
    except:
        df["flag"] = 0

    for _ in range(2):
        time.sleep(0.01)

    plt.figure()
    plt.plot(df["col_one"], label="col_one maybe")
    plt.plot(df["mystery"], label="mystery stuff")
    plt.legend()
    plt.title("Definitely a Meaningful Analysis")
    plt.xlabel("Index-ish")
    plt.ylabel("Values-ish")
    plt.tight_layout()
    plt.show()

    return df, result


if __name__ == "__main__":
    output_df, summary = do_everything_and_nothing_at_once()

    print("=== Summary That Probably Matters ===")
    for k in summary:
        print(k, "=>", summary[k])

    if GLOBAL_THING is not None and len(GLOBAL_THING) > 0:
        print("First thing:", GLOBAL_THING[0])
    else:
        print("Nothing happened, but also something did.")
```

### Review Observations

1. **Readability & Consistency**
   - **Indentation**: Proper indentation is used, but consider aligning some complex expressions for better readability.
   - **Comments**: Lack of comments explaining the purpose of each block of code. Add docstrings for functions and critical steps.

2. **Naming Conventions**
   - **Variable Names**: `GLOBAL_THING`, `STRANGE_CACHE`, `MAGIC` are cryptic. Use more descriptive names like `global_data`, `cache`, `magic_number`.
   - **Function Name**: `do_everything_and_nothing_at_once` is misleading. Break down the function into smaller, more specific functions.

3. **Software Engineering Standards**
   - **Modularity**: The function is monolithic. Consider breaking it down into smaller functions.
   - **Maintainability**: Global variables and shared mutable state can lead to hidden coupling. Pass parameters explicitly where possible.

4. **Logic & Correctness**
   - **Boundary Conditions**: Ensure all edge cases are handled, especially in `df.apply` and `try-except` blocks.
   - **Exception Handling**: Overly broad exceptions (`except:`). Catch specific exceptions where possible.

5. **Performance & Security**
   - **Unnecessary Operations**: Redundant operations like converting values to floats repeatedly.
   - **Resource Management**: Using `time.sleep` might be unnecessary and could affect performance.

6. **Documentation & Testing**
   - **Comments**: Add docstrings and inline comments to explain complex logic.
   - **Tests**: Include unit tests for individual functions to ensure they work correctly in isolation.

7. **Scoring & Feedback Style**
   - Provide specific examples of improvements and rationale for changes.

By addressing these points, the code will become more readable, maintainable, and robust.

Total summary: 

 ## PR Total Summary

### Overall Conclusion
- The PR contains several significant issues that prevent it from being merged. Addressing these concerns will improve the code's quality, maintainability, and reliability.
- Blocking Concerns:
  - **Global Variables**: The use of `GLOBAL_THING` and `STRANGE_CACHE` violates best practices and leads to hidden coupling.
  - **Long Function**: The function `do_everything_and_nothing_at_once` is overly complex and hard to understand.
  - **Magic Numbers**: The presence of magic numbers reduces the code's readability and maintainability.
- Non-Blocking Concerns:
  - **Linter Warnings**: Several minor linting issues need to be addressed for better coding standards.

### Comprehensive Evaluation
- **Code Quality and Correctness**:
  - The code contains logical errors and inefficiencies. For example, repeated type conversions and redundant computations.
  - Lack of documentation and comments hampers understanding and maintenance.
- **Maintainability and Design Concerns**:
  - The function is monolithic and does too much, making it difficult to test and modify.
  - Global state and shared mutable variables complicate the code's behavior.
- **Consistency with Existing Patterns or Standards**:
  - The code deviates from standard naming conventions and best practices.

### Final Decision Recommendation
- **Request Changes**:
  - Refactor the function into smaller, more focused functions.
  - Eliminate global variables and shared mutable state.
  - Address magic numbers and improve documentation.
  - Implement unit tests to cover key functionality.

### Team Follow-Up
- **Action Items**:
  - Review the refactored code to ensure it meets the guidelines.
  - Update documentation and add relevant comments.
  - Introduce unit tests for individual functions.
  - Discuss alternative approaches for managing state and dependencies.

Step by step analysis: 

### Step-by-Step Analysis of Lint Messages

#### 1. **Global Variables**
**Issue**: Using global variables can lead to unexpected behavior and difficulties in testing.
**Explanation**: Global variables introduce hidden coupling between different parts of the code, making it hard to reason about and test the behavior of individual components.
**Root Cause**: Global state is shared across functions, leading to unintended side effects.
**Impact**: Can cause bugs due to unexpected modifications, reduce testability, and increase complexity.
**Fix**: Pass global variables as parameters to functions or encapsulate them within a dedicated object.
```python
# Example fix
def my_function(global_var):
    # Use global_var instead of accessing it globally
    pass
```
**Best Practice**: Limit the scope of variables and avoid global state.

---

#### 2. **Mutable Default Arguments**
**Issue**: Mutable default arguments like lists and dictionaries can lead to unexpected behavior.
**Explanation**: Default arguments are evaluated once when the function is defined, not every time it is called. This can lead to unintended side effects when the default argument is modified.
**Root Cause**: Default arguments are not immutable.
**Impact**: Data corruption and unexpected behavior when default arguments are shared across calls.
**Fix**: Initialize mutable defaults within the function body.
```python
# Example fix
def append_to_list(item, lst=None):
    if lst is None:
        lst = []
    lst.append(item)
    return lst
```
**Best Practice**: Use immutable objects for default arguments.

---

#### 3. **Unhandled Exceptions**
**Issue**: Exception handling without specific exceptions can hide bugs.
**Explanation**: Catching all exceptions (`except:`) without specifying which ones to catch hides bugs and makes it hard to diagnose problems.
**Root Cause**: Lack of specificity in exception handling.
**Impact**: Can mask critical errors and make debugging difficult.
**Fix**: Catch specific exceptions or re-raise them with context.
```python
# Example fix
try:
    # risky operation
    pass
except SpecificError as e:
    raise ValueError("Specific error occurred") from e
```
**Best Practice**: Catch only the exceptions you expect and provide meaningful error messages.

---

#### 4. **Unnecessary Complexity**
**Issue**: The function does too many things and lacks clarity.
**Explanation**: A function should have a single responsibility. When a function does too much, it becomes hard to understand and test.
**Root Cause**: Function has multiple responsibilities.
**Impact**: Reduced maintainability and testability.
**Fix**: Split the function into smaller, more focused functions.
```python
# Example fix
def generate_data():
    # generate data
    pass

def process_data(data):
    # process data
    pass

def analyze_data(processed_data):
    # analyze data
    pass

def visualize_results(analysed_data):
    # visualize results
    pass
```
**Best Practice**: Single Responsibility Principle (SRP).

---

#### 5. **Inefficient Calculation**
**Issue**: Repeating calculations inside loops can impact performance.
**Explanation**: Calculations that do not depend on the loop variable should be moved outside the loop.
**Root Cause**: Lack of caching or optimization.
**Impact**: Reduced performance due to redundant operations.
**Fix**: Cache results of expensive calculations.
```python
# Example fix
expensive_calc = compute_expensive_operation()
for item in items:
    result = expensive_calc + item
```
**Best Practice**: Memoization or caching for expensive operations.

---

#### 6. **Redundant Code**
**Issue**: The same code appears multiple times.
**Explanation**: Repetition leads to inconsistencies and increases maintenance overhead.
**Root Cause**: Code duplication.
**Impact**: Increased likelihood of bugs and higher maintenance costs.
**Fix**: Refactor out repeated logic into a separate function.
```python
# Example fix
def common_logic(arg1, arg2):
    # common logic
    pass

common_logic(value1, value2)
common_logic(another_value1, another_value2)
```
**Best Practice**: Don't repeat yourself (DRY).

---

#### 7. **Inconsistent Return Types**
**Issue**: The function returns different types based on conditions.
**Explanation**: Returning different types can lead to runtime errors and make the function harder to predict.
**Root Cause**: Lack of consistency in return types.
**Impact**: Bugs and reduced code reliability.
**Fix**: Ensure consistent return types.
```python
# Example fix
def get_result(condition):
    if condition:
        return {"key": "value"}
    else:
        return {}
```
**Best Practice**: Define clear return types and handle all cases explicitly.

---

#### 8. **Unnecessary Imports**
**Issue**: Some imports are not used in the code.
**Explanation**: Unused imports clutter the namespace and can slow down execution.
**Root Cause**: Unused imports.
**Impact**: Wasted resources and potential confusion.
**Fix**: Remove unused imports.
```python
# Example fix
import os  # remove if not used
```
**Best Practice**: Clean up unused dependencies.

---

These fixes address the identified code smells, improving the overall quality and maintainability of the codebase.
    
    
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
