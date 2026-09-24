- Code Smell Type: Mutable Default Arguments
- Problem Location: `def do_everything_and_nothing_at_once(x=None, y=[], z={"a": 1}):`
- Detailed Explanation: In Python, default arguments are evaluated once at definition time, not at execution time. Using mutable objects like lists (`[]`) or dictionaries (`{}`) as defaults means that if the function modifies these objects, the changes persist across subsequent calls to the function. This leads to unpredictable behavior and difficult-to-track bugs.
- Improvement Suggestions: Use `None` as the default value and initialize the mutable object inside the function body.
  Example: `def do_everything_and_nothing_at_once(x=None, y=None, z=None):` followed by `y = y if y is not None else []`.
- Priority Level: High

- Code Smell Type: Violation of Single Responsibility Principle (God Function)
- Problem Location: `do_everything_and_nothing_at_once`
- Detailed Explanation: The function is attempting to handle data generation, business logic/transformation, statistical analysis, caching, and data visualization all in one block. This makes the code nearly impossible to unit test, difficult to maintain, and reduces readability.
- Improvement Suggestions: Break the function into smaller, focused functions:
    1. `generate_data(x)`: Handles the initial list and DataFrame creation.
    2. `calculate_metrics(df)`: Handles the "mystery" and "normalized" column logic.
    3. `get_summary_statistics(df)`: Returns the result dictionary.
    4. `plot_results(df)`: Handles the Matplotlib logic.
- Priority Level: High

- Code Smell Type: Poor Naming Conventions
- Problem Location: `do_everything_and_nothing_at_once`, `GLOBAL_THING`, `STRANGE_CACHE`, `mystery`, `weird_sum`, `something_useless`
- Detailed Explanation: The names are non-descriptive or intentionally vague. Names like "do_everything_and_nothing" or "mystery" provide no semantic meaning regarding the purpose of the data or the intent of the operation, forcing the maintainer to reverse-engineer the logic to understand the goal.
- Improvement Suggestions: Rename variables and functions to reflect their actual purpose (e.g., `process_sensor_data`, `normalized_score`, `total_weighted_sum`).
- Priority Level: Medium

- Code Smell Type: Inefficient Data Processing (Anti-pattern)
- Problem Location: `for i in range(len(df)): ... df.iloc[i]["mystery"]`
- Detailed Explanation: Iterating through a pandas DataFrame using a `for` loop and `iloc` is extremely slow and defeats the purpose of using pandas. This is a "vectorization" failure. The logic inside the loop can be achieved using `np.where` or boolean indexing, which are orders of magnitude faster.
- Improvement Suggestions: Replace the loop with a vectorized operation:
  `weird_sum = df.loc[df["mystery"] > 0, "mystery"].sum() + df.loc[df["mystery"] <= 0, "col_three"].abs().sum()`
- Priority Level: Medium

- Code Smell Type: Bare Except Clauses / Silent Failures
- Problem Location: `except: pass` and `except Exception as e: weird_sum += 0`
- Detailed Explanation: Using `except:` without specifying an exception type catches everything, including `KeyboardInterrupt` and `SystemExit`. Furthermore, silently passing or adding 0 masks potential bugs (like TypeErrors or ValueErrors) that should be fixed rather than ignored.
- Improvement Suggestions: Catch specific exceptions (e.g., `ValueError`, `TypeError`) and log the error or handle it explicitly.
- Priority Level: Medium

- Code Smell Type: Use of Global State
- Problem Location: `global GLOBAL_THING` and `STRANGE_CACHE`
- Detailed Explanation: Relying on global variables makes the function non-deterministic and creates tight coupling between different parts of the program. It makes the code thread-unsafe and complicates testing because the state persists between test cases.
- Improvement Suggestions: Pass required state as arguments to the function and return the updated state as part of the return value.
- Priority Level: Low