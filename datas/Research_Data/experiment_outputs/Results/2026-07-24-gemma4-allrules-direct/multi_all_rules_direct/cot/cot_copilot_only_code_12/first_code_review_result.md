### Code Review

**1. Readability & Naming Conventions**
*   **Naming Style:** Variable names `resultList` and `tempStorage` use camelCase, which deviates from the Python standard (PEP 8) of using `snake_case`.
*   **Vague Naming:** `DATAFRAME` is too generic. Use a name that describes the data it contains (e.g., `sensor_data` or `metrics_df`).
*   **Magic Strings:** The column names `"A"`, `"B"`, and `"C"` are hard-coded throughout the logic. These should be defined as constants at the top of the file.

**2. Software Engineering Standards**
*   **Shared Mutable State:** The use of `global` variables (`DATAFRAME`, `resultList`, `tempStorage`) creates hidden coupling and makes the code difficult to test or reuse. Pass data explicitly as function arguments and return values.
*   **Single Responsibility:** `calcStats` is performing multiple unrelated tasks: calculating means, updating a global list, and updating a global dictionary.

**3. Logic & Correctness**
*   **Redundant Computation:** In `calcStats`, `st.mean(DATAFRAME[col])` is called twice for column "A" and appended to the list twice. This is unnecessary work inside a loop.
*   **Inefficient Logic:** The nested `if col == "A"` inside `if col in ["A", "B"]` is redundant and increases cognitive load.

**4. Performance & Security**
*   **Global State Risk:** `resultList` is never cleared. If `main()` were called multiple times in a larger application, the list would grow indefinitely, leading to memory leaks and incorrect results.

**Suggested Improvements:**
*   Refactor functions to accept the DataFrame as an argument and return the results (e.g., `def calc_stats(df):`).
*   Replace global lists/dicts with local variables returned by functions.
*   Use a dictionary or a structured object for results instead of a list of tuples to avoid "dummy" entries and improve clarity.
*   Simplify the conditional logic in `calcStats` using a mapping or a more direct loop.