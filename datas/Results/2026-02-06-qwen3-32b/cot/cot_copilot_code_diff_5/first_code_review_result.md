- **Naming Conventions**:  
  Function `functionThatDoesTooMuchAndIsNotClear` is non-descriptive and negative. Rename to `generate_student_analysis_report` to reflect intent clearly.

- **Global Variables**:  
  Avoid `GLOBAL_DF` and `ANOTHER_GLOBAL`—they create hidden dependencies and reduce testability. Pass data as function parameters instead.

- **Random Value Assignment**:  
  `random.randint(0, 10)` is called once per column, applying the *same value* to every row (e.g., all rows get `+5`). For per-row randomness, use vectorized operations like `df['ScorePlusRandom'] = df['Score'] + pd.Series([random.randint(0,10) for _ in range(len(df))])`.

- **Single Responsibility Violation**:  
  The function handles data creation, transformation, analysis, and output. Split into focused functions (e.g., `create_sample_data()`, `add_random_scores()`, `calculate_mean_age()`).

- **Redundant Logic**:  
  The age range check (`if mean_age > 20: if mean_age < 50: ...`) is clearer as `if 20 < mean_age < 50: ...`. Avoid nested conditionals where unnecessary.

- **Documentation**:  
  Add a docstring explaining the function’s purpose and inputs/outputs. Example:  
  ```python
  def generate_student_analysis_report():
      """Analyze student data, add randomized scores, and print summary statistics."""
  ```