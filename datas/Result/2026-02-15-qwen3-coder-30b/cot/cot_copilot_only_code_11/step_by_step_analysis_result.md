1. **Magic Number '40' in `filter_high_scores()`**
   - **Issue**: A magic number `40` is used directly in the code without explanation.
   - **Root Cause**: The value has no semantic meaning and was hardcoded.
   - **Impact**: Reduces readability; future modifications may introduce bugs.
   - **Fix**: Replace with a named constant.
     ```python
     HIGH_SCORE_THRESHOLD = 40
     if score > HIGH_SCORE_THRESHOLD:
         ...
     ```
   - **Best Practice**: Always name numeric constants for clarity.

2. **Magic Number '50' in `process_misc()`**
   - **Issue**: Another magic number `50` appears without context.
   - **Root Cause**: Same as above — lack of descriptive naming.
   - **Impact**: Makes assumptions unclear.
   - **Fix**: Extract into a constant.
     ```python
     DEFAULT_THRESHOLD = 50
     if value >= DEFAULT_THRESHOLD:
         ...
     ```
   - **Best Practice**: Avoid magic numbers in favor of meaningful identifiers.

3. **Duplicate Access Pattern for `DATA['users']`**
   - **Issue**: Multiple functions access `DATA['users']` repeatedly.
   - **Root Cause**: Repetitive code structure rather than abstraction.
   - **Impact**: Increases risk of inconsistency if accessed differently.
   - **Fix**: Create a helper function.
     ```python
     def get_users(data):
         return data['users']
     ```
   - **Best Practice**: DRY – Don’t Repeat Yourself.

4. **Nested Conditional Checks in `main()`**
   - **Issue**: Deeply nested if statements complicate logic flow.
   - **Root Cause**: Lack of early exits or logical simplification.
   - **Impact**: Harder to debug and maintain.
   - **Fix**: Use guard clauses or refactor conditionals.
     ```python
     if not flag_a:
         return
     if not flag_b:
         return
     # proceed with core logic
     ```
   - **Best Practice**: Flatten control structures for readability.

5. **Hardcoded String 'X' in `main()`**
   - **Issue**: The string `'X'` is embedded directly in code.
   - **Root Cause**: No abstraction or localization support.
   - **Impact**: Difficult to update or translate later.
   - **Fix**: Define as a constant.
     ```python
     MODE_X = 'X'
     print(f"Mode {MODE_X}")
     ```
   - **Best Practice**: Externalize user-facing strings.

6. **Global State Usage (`DATA`)**
   - **Issue**: Functions depend on global variable `DATA`.
   - **Root Cause**: Tight coupling between components.
   - **Impact**: Limits testability and modularity.
   - **Fix**: Pass data as parameters.
     ```python
     def filter_high_scores(data, threshold=40):
         ...
     ```
   - **Best Practice**: Prefer dependency injection over global access.

7. **Unreachable Code After Else Clause**
   - **Issue**: Some code paths are unreachable due to nested conditionals.
   - **Root Cause**: Overly complex branching logic.
   - **Impact**: Confusing behavior and potential bugs.
   - **Fix**: Review and simplify conditional structure.
     ```python
     if condition_a:
         ...
     elif condition_b:
         ...
     # Remove redundant branches
     ```
   - **Best Practice**: Ensure all code paths are logically reachable.

8. **Lack of Explicit Returns**
   - **Issue**: Functions implicitly return `None`.
   - **Root Cause**: Missing explicit return statements.
   - **Impact**: Minor readability issue.
   - **Fix**: Be intentional about returns.
     ```python
     def example():
         if condition:
             return True
         return False
     ```
   - **Best Practice**: Make return behavior explicit.

9. **Long Function (`main`)**
   - **Issue**: Main function combines too many responsibilities.
   - **Root Cause**: Violation of single responsibility principle.
   - **Impact**: Difficult to test or reuse.
   - **Fix**: Break into smaller, focused functions.
     ```python
     def run_processing_flow(data):
         avg_scores = calculate_averages(data)
         filtered = filter_high_scores(avg_scores)
         ...
     ```
   - **Best Practice**: Keep functions small and focused.

10. **Poor Naming (`process_misc`)**
    - **Issue**: Function name lacks clarity.
    - **Root Cause**: Generic or vague naming.
    - **Impact**: Misleading or confusing to others.
    - **Fix**: Rename for better understanding.
      ```python
      def categorize_miscellaneous_items(...): ...
      ```
    - **Best Practice**: Use descriptive, domain-specific names.

11. **Missing Input Validation**
    - **Issue**: No checks for missing or malformed data.
    - **Root Cause**: Assumptions about input format.
    - **Impact**: Risk of runtime exceptions.
    - **Fix**: Validate before processing.
      ```python
      assert 'users' in data
      assert isinstance(data['users'], list)
      ```
    - **Best Practice**: Defensive programming improves robustness.

12. **Lack of Comments or Documentation**
    - **Issue**: No inline comments or docstrings.
    - **Root Cause**: Lack of self-documenting code.
    - **Impact**: Slower onboarding and debugging.
    - **Fix**: Add docstrings and inline explanations.
      ```python
      def filter_high_scores(data, threshold=40):
          """Filter users whose scores exceed threshold."""
          ...
      ```
    - **Best Practice**: Document interfaces and logic clearly.

13. **Hardcoded String Literals**
    - **Issue**: String literals are hardcoded throughout the codebase.
    - **Root Cause**: No abstraction for UI or config text.
    - **Impact**: Inflexible and hard to maintain.
    - **Fix**: Centralize such values.
      ```python
      MODE_LABEL = "Mode X"
      ```
    - **Best Practice**: Treat UI/config strings as configurable resources.