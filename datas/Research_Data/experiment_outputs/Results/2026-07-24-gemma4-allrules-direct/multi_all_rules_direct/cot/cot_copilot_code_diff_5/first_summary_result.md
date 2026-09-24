## PR Summary

*   **Key changes**: Introduced a new data analysis module `data_analysis.py` that creates a sample DataFrame, performs basic calculations, and prints descriptive statistics.
*   **Purpose of changes**: Initial implementation of data analysis functionality.
*   **Items to confirm**: The current implementation contains several architectural and coding standard issues (detailed in the review below) that should be addressed before merging.

---

## Code Review

### 1. Readability & Consistency
*   **Naming Conventions**: The function name `functionThatDoesTooMuchAndIsNotClear` is non-descriptive and violates standard Python naming conventions (should be `snake_case`). It should be renamed to reflect its actual purpose (e.g., `analyze_student_scores`).

### 2. Software Engineering Standards
*   **Single Responsibility Principle**: The function `functionThatDoesTooMuchAndIsNotClear` violates this principle. It handles data creation, data transformation, business logic (age validation), and I/O (printing) all in one block. These should be split into separate functions (e.g., `load_data()`, `calculate_metrics()`, `print_report()`).
*   **Modularization**: The code is written as a script rather than a reusable module.

### 3. Logic & Correctness
*   **Deeply Nested Logic**: The age validation logic uses nested `if/else` blocks. This increases cognitive load.
    *   *Recommendation*: Use guard clauses or a flatter structure to improve readability.

### 4. Performance & Security
*   **Inefficient Loop/Operation**: While not a loop, the repeated calls to `random.randint` for similar columns suggest a lack of vectorized approach or a missing loop for repetitive transformations.

### 5. RAG Rules Violations

*   **Shared Mutable State**: 
    *   The use of `GLOBAL_DF = None` and the `global` keyword inside the function introduces hidden coupling and makes the code difficult to test and reason about. 
    *   *Recommendation*: Pass the DataFrame as an argument to functions and return the modified DataFrame.
*   **Broad Exception Handling**: 
    *   The code uses `except Exception as e:`, which catches all errors (including keyboard interrupts or system exits) and hides the specific cause of failure.
    *   *Recommendation*: Catch specific exceptions (e.g., `KeyError`, `TypeError`) or remove the try-except block if the operations are guaranteed to be safe.
*   **Implicit Truthiness/Magic Values**: 
    *   The use of `ANOTHER_GLOBAL = "分析開始"` acts as a magic string. While simple here, constants should be clearly defined and used purposefully.
*   **Environment-Dependent Logic**: 
    *   The use of `random.randint` without a seed makes the output non-deterministic, which will make unit testing difficult.
    *   *Recommendation*: Allow an optional seed parameter for reproducibility.

### Summary of Required Changes
1.  **Refactor** the monolithic function into smaller, focused functions.
2.  **Remove** global variables (`GLOBAL_DF`) in favor of explicit parameter passing.
3.  **Rename** functions to follow `snake_case` and be descriptive.
4.  **Replace** the broad `except Exception` with specific error handling.
5.  **Flatten** the nested conditional logic for age checking.