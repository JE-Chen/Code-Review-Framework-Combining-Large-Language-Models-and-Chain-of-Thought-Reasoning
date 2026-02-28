# Code Review Summary

## Code Smell Type: Global State Usage
**Problem Location:** `loadData()`, `calcStats()`, `plotData()` functions using `global DATAFRAME`, `resultList`, and `tempStorage`.

**Detailed Explanation:** 
The code heavily relies on global variables (`DATAFRAME`, `resultList`, `tempStorage`) which makes the program harder to reason about, test, and maintain. This creates tight coupling between functions, reduces modularity, and introduces side effects that can lead to unpredictable behavior.

**Improvement Suggestions:**
- Pass data explicitly through parameters instead of relying on global state
- Return computed values from functions rather than modifying global variables
- Consider encapsulating related functionality into classes

**Priority Level:** High

---

## Code Smell Type: Magic Strings/Numbers
**Problem Location:** `"A"`, `"B"`, `"C"`, `"X"`, `"Y"`, `"Z"`, `7` in `plotData()` and `calcStats()`.

**Detailed Explanation:**
Hardcoded strings and numbers make the code brittle and difficult to modify. If column names or bin count changes, these values need to be manually updated in multiple places. It also reduces readability and increases maintenance overhead.

**Improvement Suggestions:**
- Define constants for column names and other fixed values
- Use configuration files or parameters for configurable values like bin count
- Extract string literals into named constants

**Priority Level:** Medium

---

## Code Smell Type: Long Function
**Problem Location:** `calcStats()` function spans 15 lines with complex conditional logic.

**Detailed Explanation:**
This function violates the Single Responsibility Principle by performing multiple tasks: calculating statistics, storing results, and managing temporary storage. The nested conditionals make it hard to understand and maintain. As complexity grows, debugging and testing become increasingly difficult.

**Improvement Suggestions:**
- Break down `calcStats()` into smaller, focused functions
- Separate concerns such as calculation, storage, and result formatting
- Consider using data structures or pattern matching for cleaner conditional logic

**Priority Level:** High

---

## Code Smell Type: Inconsistent Naming Conventions
**Problem Location:** `DATAFRAME`, `resultList`, `tempStorage` vs. `meanA`, `meanB`, etc.

**Detailed Explanation:**
Inconsistent naming styles (PascalCase vs snake_case) reduce code readability and make it harder for new developers to understand the codebase. Team-wide consistency helps in maintaining code quality over time.

**Improvement Suggestions:**
- Adopt one consistent naming convention (preferably snake_case as per PEP8)
- Apply uniform naming rules across all identifiers
- Use linters to enforce naming standards automatically

**Priority Level:** Medium

---

## Code Smell Type: Duplicate Code
**Problem Location:** Repeated logic for calculating mean in `calcStats()`.

**Detailed Explanation:**
There's redundant computation where the same statistic (mean) is calculated twice for column "A". This duplication can introduce inconsistencies and makes future modifications error-prone.

**Improvement Suggestions:**
- Remove duplicate calculations
- Refactor repeated patterns into reusable helper functions
- Use a loop or mapping approach for similar operations

**Priority Level:** Medium

---

## Code Smell Type: Poor Separation of Concerns
**Problem Location:** `calcStats()` mixes statistical computations, result recording, and temporary storage management.

**Detailed Explanation:**
Functions should have a single responsibility. Here, `calcStats()` performs too many different actions, making it harder to isolate bugs and write effective unit tests. Each concern should be handled by its own module or function.

**Improvement Suggestions:**
- Split into dedicated modules: data processing, statistics computation, result collection, and reporting
- Implement proper separation of concerns by assigning distinct roles to each component
- Create separate classes or modules for different responsibilities

**Priority Level:** High

---

## Code Smell Type: Lack of Input Validation
**Problem Location:** No validation of input data structure or types.

**Detailed Explanation:**
If `DATAFRAME` doesn't match expected schema, or if column types change unexpectedly, the program could crash or produce incorrect results without warning. Robust programs handle edge cases gracefully.

**Improvement Suggestions:**
- Add checks for DataFrame structure and data types
- Validate assumptions about column existence and content
- Include logging or error messages when invalid data is encountered

**Priority Level:** Medium

---

## Code Smell Type: Hardcoded Titles/Labels
**Problem Location:** `"Histogram of A (for no reason)"` in `plotData()`.

**Detailed Explanation:**
Hardcoded titles reduce flexibility and make reusing the plotting logic more difficult. Comments suggest that even the title itself lacks justification, indicating poor design decisions.

**Improvement Suggestions:**
- Make chart labels configurable via parameters or config files
- Generate dynamic titles based on actual data or context
- Allow customization of visual elements for better reusability

**Priority Level:** Low

---

## Code Smell Type: Unused Imports / Redundant Dependencies
**Problem Location:** Imported but unused libraries (`matplotlib.pyplot`).

**Detailed Explanation:**
While `matplotlib.pyplot` is imported, it's only used once in `plotData()` and not fully utilized elsewhere. Including unnecessary imports increases load times and suggests incomplete use of features.

**Improvement Suggestions:**
- Remove unused imports
- Only import what you actually use
- Use selective imports to minimize dependencies

**Priority Level:** Low

---

## Code Smell Type: Non-Standard Library Usage
**Problem Location:** `statistics` library aliased as `st`.

**Detailed Explanation:**
Using an alias for standard library modules might confuse developers unfamiliar with the project. While technically acceptable, it reduces clarity unless there's a compelling reason.

**Improvement Suggestions:**
- Prefer standard names like `statistics` over aliases
- If aliasing is necessary, document the rationale clearly
- Maintain consistency with Python idioms

**Priority Level:** Low