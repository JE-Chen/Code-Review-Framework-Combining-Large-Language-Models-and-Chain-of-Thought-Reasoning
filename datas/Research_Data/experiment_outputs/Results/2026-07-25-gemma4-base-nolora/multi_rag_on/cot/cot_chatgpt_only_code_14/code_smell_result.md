- Code Smell Type: Shared Mutable State (Global Variables)
- Problem Location: `GLOBAL_DATA_THING = None`, `GLOBAL_FLAG = {"dirty": False}`, and their usage via `global` keywords in `make_data_somehow` and `analyze_in_a_hurry`.
- Detailed Explanation: The use of global variables to store application state creates hidden coupling between methods. This makes the code difficult to test in isolation, as the state of one test can leak into another. It also prevents the application from ever supporting multiple data sets or multiple window instances without them interfering with each other.
- Improvement Suggestions: Encapsulate the data and flags as instance attributes of the `EverythingWindow` class (e.g., `self.data` and `self.is_dirty`) or create a separate `DataManager` class to handle the state.
- Priority Level: High

- Code Smell Type: Violation of Single Responsibility Principle (God Object)
- Problem Location: `class EverythingWindow(QMainWindow)`
- Detailed Explanation: The `EverythingWindow` class is handling three distinct responsibilities: UI layout/management, data generation logic, and data analysis logic. This "God Object" pattern makes the class bloated and difficult to maintain. If the analysis logic changes, you are forced to modify the UI class.
- Improvement Suggestions: Separate the concerns into three layers:
    1. A **UI Layer** (the QMainWindow) that only handles widget placement and event triggering.
    2. A **Service/Logic Layer** for data analysis calculations.
    3. A **Data Layer** for generating or fetching the data.
- Priority Level: High

- Code Smell Type: Unclear/Non-Descriptive Naming
- Problem Location: `GLOBAL_DATA_THING`, `make_data_somehow`, `analyze_in_a_hurry`, `do_something_questionable`, `weird_counter`, `weird_metric`.
- Detailed Explanation: Names like "somehow," "hurry," and "questionable" provide no semantic meaning regarding what the code actually does. This forces a developer to read the entire implementation to understand the intent, significantly slowing down maintenance and increasing the risk of bugs.
- Improvement Suggestions: Use descriptive, action-oriented names. For example: `generate_random_dataset()`, `calculate_data_metrics()`, `process_flag_status()`, and `analysis_iteration_count`.
- Priority Level: Medium

- Code Smell Type: Poor Exception Handling (Bare Except)
- Problem Location: `except: GLOBAL_DATA_THING = None` and `except: pass` inside `analyze_in_a_hurry`.
- Detailed Explanation: Using bare `except:` blocks catches all exceptions, including `KeyboardInterrupt` and `SystemExit`, and silences them. This hides bugs (like `KeyError` or `TypeError`) that should be fixed rather than ignored, making debugging nearly impossible.
- Improvement Suggestions: Catch specific exceptions (e.g., `ValueError`, `TypeError`, `pd.errors.EmptyDataError`) and log the error using the `logging` module instead of silently passing.
- Priority Level: Medium

- Code Smell Type: Performance Bottleneck (Inefficient DataFrame Iteration)
- Problem Location: `for i in range(len(df)): total += df.iloc[i]["mix"]`
- Detailed Explanation: Using a Python `for` loop with `.iloc` to iterate over a pandas DataFrame is extremely slow. Pandas is designed for vectorized operations. For large datasets, this will cause the UI to freeze (especially since it's running on the main GUI thread).
- Improvement Suggestions: Use vectorized pandas operations. The entire loop can be replaced with: `total = df.loc[df["mix"] > 0, "mix"].sum() + df.loc[df["mix"] <= 0, "gamma"].abs().sum()`.
- Priority Level: Medium