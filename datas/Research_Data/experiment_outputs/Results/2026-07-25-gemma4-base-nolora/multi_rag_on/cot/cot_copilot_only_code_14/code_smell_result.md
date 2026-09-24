- Code Smell Type: Excessive Use of Global State
- Problem Location: `dataFrameLike`, `resultCache`, `textOutput`, `tableWidget`, `labelStatus` (and their usage via `global` keywords in every function).
- Detailed Explanation: The application relies entirely on global variables to share state between the UI and the logic. This creates tight coupling, makes the code nearly impossible to unit test (as functions have hidden dependencies), and increases the risk of side-effect bugs. In a GUI application, this pattern prevents the ability to instantiate multiple windows or independent data sessions.
- Improvement Suggestions: Encapsulate the application logic and UI within a class (e.g., `class DataAnalyzerApp(QWidget)`). Store the data and widgets as instance attributes (`self.data`, `self.result_cache`).
- Priority Level: High

- Code Smell Type: Violation of Single Responsibility Principle (SRP) / Tight Coupling
- Problem Location: `showData()`, `showResults()`, `updateStatus()`
- Detailed Explanation: The logic functions are directly manipulating UI widgets (e.g., `tableWidget.setItem`, `textOutput.append`). The "Analysis" logic is intertwined with the "Presentation" logic. If the UI framework were changed or the layout modified, the core logic functions would break.
- Improvement Suggestions: Separate the data processing from the UI updates. Functions like `analyzeData` should return a result object or dictionary, and a separate UI-handler method should take that result and update the widgets.
- Priority Level: Medium

- Code Smell Type: Redundant Computation / Inefficient Logic
- Problem Location: `analyzeData()`
  - `resultCache["meanNumAgain"] = statistics.mean(nums)`
  - `resultCache["medianValPlus42"] = statistics.median(vals) + 42`
- Detailed Explanation: The code calculates the mean and median multiple times for the same dataset within the same function call. This is computationally wasteful and creates redundant keys in the result cache that provide no additional semantic value.
- Improvement Suggestions: Calculate the value once, store it in a local variable, and reuse that variable for subsequent assignments.
- Priority Level: Low

- Code Smell Type: Unclear Naming Conventions
- Problem Location: `dataFrameLike`, `btnGen`, `btnAna`, `btnShow`, `btnRes`
- Detailed Explanation: Variable names are either overly vague (`btnGen`) or use non-standard naming conventions (mixing camelCase with abbreviations). `dataFrameLike` is a confusing name that describes what the variable "resembles" rather than what it "is" (e.g., `raw_data`).
- Improvement Suggestions: Use PEP 8 compliant `snake_case` for variables and functions. Use descriptive names: `btn_generate_data`, `btn_analyze_data`, `dataset`.
- Priority Level: Low