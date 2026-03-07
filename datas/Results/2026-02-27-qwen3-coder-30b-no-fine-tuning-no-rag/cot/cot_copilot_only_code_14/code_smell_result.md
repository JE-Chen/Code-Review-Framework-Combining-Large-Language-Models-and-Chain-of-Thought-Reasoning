### Code Smell Type: Global State Usage
- **Problem Location:** All global variables (`dataFrameLike`, `resultCache`, `textOutput`, `tableWidget`, `labelStatus`)
- **Detailed Explanation:** The use of global variables makes the code harder to reason about, debug, and test. It breaks encapsulation by allowing any function to modify shared state without clear boundaries. This leads to tight coupling between functions and increases the risk of side effects and unexpected behavior during execution.
- **Improvement Suggestions:** Replace global variables with local or instance variables within a class structure. Encapsulate UI components and data in a dedicated class like `MainWindow` or `DataManager`.
- **Priority Level:** High

---

### Code Smell Type: Magic Numbers
- **Problem Location:** Hardcoded values such as `100`, `50`, `37`, `5`, `10`, `42`
- **Detailed Explanation:** These numbers lack context and meaning, making the code less readable and maintainable. For example, `5` and `10` appear to be thresholds but are not named, and `42` seems arbitrary. Changing these would require searching through the entire codebase.
- **Improvement Suggestions:** Define constants for key numeric values using descriptive names (e.g., `MAX_DATA_ROWS = 37`, `THRESHOLD_MEAN_HIGH = 50`, `ADDITIONAL_MEDIAN_VALUE = 42`). Use them consistently throughout the code.
- **Priority Level:** Medium

---

### Code Smell Type: Duplicate Logic / Redundant Calculations
- **Problem Location:** In `analyzeData()` function:
  - `statistics.mean(nums)` is called twice and assigned to different keys.
  - `statistics.median(vals)` is used twice.
- **Detailed Explanation:** The repeated calls to statistical functions lead to unnecessary computational overhead. If the dataset is large, this can impact performance. Also, duplication reduces maintainability — changes to one calculation must be manually synchronized across multiple lines.
- **Improvement Suggestions:** Store results from expensive operations in temporary variables before assigning them to cache entries. Refactor redundant computations into helper methods.
- **Priority Level:** Medium

---

### Code Smell Type: Violation of Single Responsibility Principle
- **Problem Location:** Functions `generateData`, `analyzeData`, `showData`, `showResults`, `updateStatus` perform multiple tasks.
- **Detailed Explanation:** Each function handles more than one responsibility. For instance, `analyzeData` both performs analysis and updates internal state, while `showData` modifies the GUI directly. This makes the code harder to test, reuse, and understand.
- **Improvement Suggestions:** Break down each function into smaller, focused units. For example, separate data generation logic from display logic, and isolate business logic from UI interactions.
- **Priority Level:** High

---

### Code Smell Type: Poor Naming Conventions
- **Problem Location:** Variables like `dataFrameLike`, `resultCache`, `textOutput`, `tableWidget`, `labelStatus`
- **Detailed Explanation:** While some names are somewhat descriptive, others are ambiguous or misleading. For example, `dataFrameLike` doesn't clearly indicate its purpose or type. Similarly, `resultCache` is vague; it's unclear what kind of caching is happening here.
- **Improvement Suggestions:** Rename variables to reflect their roles and types. Examples:
  - `dataFrameLike` → `raw_data_list`
  - `resultCache` → `analysis_results`
  - `textOutput` → `output_text_area`
  - `tableWidget` → `data_table_widget`
  - `labelStatus` → `status_label`
- **Priority Level:** Medium

---

### Code Smell Type: Tight Coupling Between Components
- **Problem Location:** Direct access to UI elements via globals inside functions (`showData`, `showResults`)
- **Detailed Explanation:** Functions directly manipulate UI widgets (`QTextEdit`, `QTableWidget`) rather than being passed references or using event-driven patterns. This creates tight coupling between logic and presentation layers, reducing modularity and testability.
- **Improvement Suggestions:** Introduce a model-view-controller (MVC) or similar architectural pattern where views don’t directly interact with logic. Pass required objects (widgets) to functions instead of relying on global scope.
- **Priority Level:** High

---

### Code Smell Type: Lack of Input Validation
- **Problem Location:** No checks on whether data has been generated or if inputs are valid before processing.
- **Detailed Explanation:** If `analyzeData()` is called when no data exists, or if the user interacts with buttons out-of-order, undefined behaviors may occur. There’s no error handling for invalid states.
- **Improvement Suggestions:** Add validation at entry points, e.g., check `len(dataFrameLike)` before accessing indices, and ensure that `dataFrameLike` is populated before running `analyzeData`. Raise exceptions or return error codes when needed.
- **Priority Level:** Medium

---

### Code Smell Type: Inconsistent Use of Lambda Expression
- **Problem Location:** `btnAna.clicked.connect(lambda: [analyzeData(), updateStatus()])`
- **Detailed Explanation:** Using lambda for simple sequences of actions can make debugging harder and is generally discouraged unless necessary. It also makes testing difficult because lambdas aren't easily unit tested.
- **Improvement Suggestions:** Create a dedicated handler method that encapsulates both actions. Example:
  ```python
  def handleAnalyzeClick():
      analyzeData()
      updateStatus()
  ```
  Then connect as `btnAna.clicked.connect(handleAnalyzeClick)`.
- **Priority Level:** Medium

---

### Code Smell Type: Lack of Comments or Documentation
- **Problem Location:** Entire file lacks inline comments explaining the intent behind logic or UI flow.
- **Detailed Explanation:** Without documentation, even experienced developers might struggle to quickly grasp how various parts relate to each other. This slows down onboarding and maintenance.
- **Improvement Suggestions:** Add docstrings to functions describing parameters, return values, and side effects. Comment complex blocks of logic to explain reasoning or algorithmic decisions.
- **Priority Level:** Low

---