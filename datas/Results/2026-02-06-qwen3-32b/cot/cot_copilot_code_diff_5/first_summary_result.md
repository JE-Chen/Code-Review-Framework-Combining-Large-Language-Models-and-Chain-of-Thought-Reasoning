# Code Review: data_analysis.py

## Critical Issues
- **Global Variables**: `GLOBAL_DF` and `ANOTHER_GLOBAL` violate encapsulation principles. This creates hidden dependencies and prevents testability.
- **Poor Function Naming**: `functionThatDoesTooMuchAndIsNotClear` is unprofessional, non-descriptive, and negative. Names should reflect *intent*, not implementation flaws.
- **Broad Exception Handling**: `except Exception` masks all errors (e.g., potential `KeyError` if columns don't exist). Should handle specific exceptions or fail gracefully.

## Major Issues
- **Function Overload**: Single function handles data creation, transformation, analysis, and output. Violates Single Responsibility Principle.
- **Non-Deterministic Output**: Two separate `random.randint()` calls produce unpredictable results (e.g., same random value twice). Makes output non-repeatable.
- **Inconsistent Language**: Mixed English code + Chinese comments/strings (e.g., `"分析開始"`). Creates confusion for non-Chinese speakers.

## Minor Issues
- **Missing Documentation**: No docstring explaining function purpose, inputs, or outputs.
- **Redundant Logic**: Duplicate pattern for adding random columns (`ScorePlusRandom` and `ScorePlusRandomAgain`).

---

## Recommendations
1. **Replace globals** with function parameters/return values.  
   *Example:*  
   ```python
   def analyze_data(df: pd.DataFrame) -> pd.DataFrame:
       # ... no globals
   ```

2. **Split monolithic function** into focused units:  
   ```python
   def create_sample_data() -> pd.DataFrame: ...
   def add_random_score_columns(df: pd.DataFrame) -> pd.DataFrame: ...
   def print_age_analysis(df: pd.DataFrame) -> None: ...
   ```

3. **Use descriptive names** (not implementation details):  
   ❌ `functionThatDoesTooMuchAndIsNotClear`  
   ✅ `generate_sample_analysis_report`

4. **Fix randomness** to ensure deterministic behavior (e.g., for testing):  
   ```python
   # Remove randomness or use seed for reproducibility
   ```

5. **Standardize language** to English for all code elements (comments, strings, variable names).

6. **Add docstrings** explaining function purpose and usage.

---

## Why This Matters
- **Testability**: Removing globals enables unit testing of core logic.
- **Maintainability**: Split functions reduce cognitive load when modifying code.
- **Reliability**: Specific exception handling prevents silent failures.
- **Team Efficiency**: Consistent naming and language reduce onboarding time.

> **Critical path**: Refactor before merging. The current code is fragile, untestable, and violates core engineering principles. Prioritize splitting the function and removing globals.  

---

## Items to Confirm
- [ ] Will the new design allow unit testing of analysis logic?
- [ ] Are Chinese strings intentional for the target audience? (If yes, ensure *all* strings are consistent)
- [ ] Does the randomness serve a purpose? (If not, remove it entirely)