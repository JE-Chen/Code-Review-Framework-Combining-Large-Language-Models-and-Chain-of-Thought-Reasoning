### Code Review

#### 1. Naming Conventions
*   **Vague Naming:** Several variables and functions use non-descriptive names that hinder maintainability:
    *   `GLOBAL_DATA_THING`, `GLOBAL_FLAG`, `EverythingWindow` (Classes/Globals).
    *   `make_data_somehow`, `analyze_in_a_hurry`, `do_something_questionable` (Methods).
    *   `a`, `b`, `c`, `v` (Local variables).
*   **Suggestion:** Rename to reflect actual purpose (e.g., `GLOBAL_DATA_THING` $\rightarrow$ `shared_dataset`, `make_data_somehow` $\rightarrow$ `generate_dataset`).

#### 2. Software Engineering Standards
*   **Global State:** The use of `global` variables (`GLOBAL_DATA_THING`, `GLOBAL_FLAG`) creates tight coupling and makes the code harder to test and debug.
*   **Modularity:** The `EverythingWindow` class handles UI layout, data generation, and business logic.
*   **Suggestion:** Move data generation and analysis logic into a separate Controller or Service class. Store the dataset as an instance attribute (`self.dataset`) rather than a global.

#### 3. Logic & Correctness
*   **Bare Except Blocks:** The code uses `except:` without specifying an exception type (e.g., in `make_data_somehow` and `analyze_in_a_hurry`). This can hide critical system errors or keyboard interrupts.
*   **UI Blocking:** `time.sleep()` is called on the main GUI thread, which will freeze the application interface during execution.
*   **Inefficient DataFrame Access:** Using `df.iloc[i]` in a `for` loop is significantly slower than using pandas vectorized operations.
*   **Suggestion:** Use specific exceptions (e.g., `ValueError`), remove `time.sleep()` or use `QThread`, and replace the `for` loop in `analyze_in_a_hurry` with a vectorized `.sum()` or `.apply()`.

#### 4. Readability & Consistency
*   **Formatting:** General indentation and structure are consistent.
*   **Comments:** The code lacks meaningful documentation or docstrings explaining the purpose of the "weird metrics" or the data structure.

#### 5. Performance & Security
*   **Resource Management:** The `Figure` is cleared and redrawn frequently; for larger datasets, this may cause memory overhead or lag.
*   **Input Validation:** There is no check to ensure `GLOBAL_DATA_THING` is actually a DataFrame before calling `.iloc` or `.mean()`, which could lead to crashes if the `try-except` block fails silently.