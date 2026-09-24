- Code Smell Type: Shared Mutable State (Global Variables)
- Problem Location: `GLOBAL_DATA_THING = None`, `GLOBAL_FLAG = {"dirty": False}`, and their usage in `make_data_somehow`, `analyze_in_a_hurry`, and `do_something_questionable`.
- Detailed Explanation: The use of global variables to store application state creates hidden coupling between methods. It makes the code difficult to test in isolation, as the state persists across different function calls and tests. It also prevents the application from ever supporting multiple windows or data sets simultaneously.
- Improvement Suggestions: Encapsulate the data and flags as instance attributes of the `EverythingWindow` class (e.g., `self.data` and `self.is_dirty`) or create a dedicated `DataManager` class to handle the state.
- Priority Level: High

- Code Smell Type: Violation of Single Responsibility Principle (God Object)
- Problem Location: `EverythingWindow` class.
- Detailed Explanation: The `EverythingWindow` class is handling three distinct responsibilities: UI layout/management, data generation logic, and data analysis logic. This makes the class bloated and difficult to maintain. If the analysis logic changes, the UI class must be modified.
- Improvement Suggestions: Separate the concerns into three layers:
    1. A `DataService` or `Analyzer` class for the math and pandas logic.
    2. A `DataGenerator` class for creating the datasets.
    3. The `EverythingWindow` class, which should only handle user input and display updates.
- Priority Level: High

- Code Smell Type: Poor Naming Conventions
- Problem Location: `GLOBAL_DATA_THING`, `make_data_somehow`, `analyze_in_a_hurry`, `do_something_questionable`, `weird_counter`, `weird_metric`.
- Detailed Explanation: The naming is non-descriptive and unprofessional. Names like "somehow," "hurry," and "questionable" provide no semantic meaning regarding what the code actually does, which hinders readability and maintainability for other developers.
- Improvement Suggestions: Use descriptive, action-oriented names. For example: `generate_dataset()`, `perform_statistical_analysis()`, `process_metadata()`, and `analysis_iteration_count`.
- Priority Level: Medium

- Code Smell Type: Improper Exception Handling (Bare Except)
- Problem Location: `except:` blocks in `make_data_somehow` and `analyze_in_a_hurry`.
- Detailed Explanation: Using bare `except:` clauses catches all exceptions, including `KeyboardInterrupt` and `SystemExit`, and silences them without logging. This hides bugs (like `KeyError` or `TypeError`) and makes debugging nearly impossible because the program fails silently or continues in an inconsistent state.
- Improvement Suggestions: Catch specific exceptions (e.g., `ValueError`, `KeyError`) and implement proper logging or user notifications when an error occurs.
- Priority Level: Medium

- Code Smell Type: Environment-Dependent Logic (Blocking UI Thread)
- Problem Location: `time.sleep(0.05)` and `time.sleep(0.03)` inside UI event handlers.
- Detailed Explanation: Calling `time.sleep()` on the main GUI thread freezes the entire application interface, making it unresponsive to user input. While the durations are short here, this pattern leads to "Application Not Responding" (ANR) errors as complexity grows.
- Improvement Suggestions: Remove unnecessary sleeps. If a delay is required for a process, use `QTimer` or move heavy computations to a separate `QThread` or `Worker` pattern.
- Priority Level: Medium