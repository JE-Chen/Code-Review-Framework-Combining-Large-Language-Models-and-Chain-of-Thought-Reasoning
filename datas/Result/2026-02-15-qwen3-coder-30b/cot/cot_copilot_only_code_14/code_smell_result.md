### Code Smell Type: Global State Dependency
- **Problem Location:** All functions (`generateData`, `analyzeData`, `showData`, `showResults`, `updateStatus`) access global variables directly.
- **Detailed Explanation:** The use of global variables like `dataFrameLike`, `resultCache`, `textOutput`, etc., makes the code tightly coupled and harder to reason about. This leads to side effects and makes testing difficult.
- **Improvement Suggestions:** Encapsulate state within a class or pass dependencies explicitly instead of relying on global scope.
- **Priority Level:** High

---

### Code Smell Type: Magic Numbers
- **Problem Location:** `range(37)` and hardcoded thresholds like `5` and `10` in conditionals.
- **Detailed Explanation:** Hardcoded values reduce flexibility and readability. If these values change, they are scattered throughout the codebase.
- **Improvement Suggestions:** Extract constants into named variables or configuration objects for better clarity and maintainability.
- **Priority Level:** Medium

---

### Code Smell Type: Duplicated Logic
- **Problem Location:** Repeated calls to `statistics.mean(nums)` and `statistics.median(vals)` inside `analyzeData`.
- **Detailed Explanation:** Calculating the same value multiple times unnecessarily increases computational cost and reduces maintainability.
- **Priority Level:** High

---

### Code Smell Type: Lack of Input Validation
- **Problem Location:** No checks on whether inputs are valid before processing.
- **Detailed Explanation:** Without validation, invalid or unexpected data can cause runtime errors or incorrect behavior.
- **Improvement Suggestions:** Add input validation at entry points and ensure data integrity before proceeding with analysis.
- **Priority Level:** High

---

### Code Smell Type: Violation of Single Responsibility Principle
- **Problem Location:** `analyzeData` performs multiple tasks including statistical computation and caching.
- **Detailed Explanation:** A function should do one thing well. Mixing responsibilities makes it harder to understand, test, and modify.
- **Improvement Suggestions:** Split `analyzeData` into smaller, focused functions such as `computeMeans`, `computeMedians`, and `cacheResults`.
- **Priority Level:** High

---

### Code Smell Type: Poor Naming Convention
- **Problem Location:** Variables like `dataFrameLike`, `resultCache`, `textOutput`, etc.
- **Detailed Explanation:** Names don't clearly convey intent or type. For example, `dataFrameLike` suggests similarity to pandas DataFrame but does not indicate actual usage or purpose.
- **Improvement Suggestions:** Use more descriptive names that reflect both the content and context of each variable.
- **Priority Level:** Medium

---

### Code Smell Type: Inefficient Data Structures
- **Problem Location:** Using list comprehension to extract columns from nested lists.
- **Detailed Explanation:** While acceptable for small datasets, iterating over rows repeatedly is inefficient when working with larger data sets.
- **Improvement Suggestions:** Consider using NumPy arrays or other optimized structures for numerical computations.
- **Priority Level:** Medium

---

### Code Smell Type: Tight Coupling Between UI and Business Logic
- **Problem Location:** Direct interaction between UI components (`QPushButton`, `QTextEdit`) and backend logic.
- **Detailed Explanation:** This design hinders reusability and testing since business logic cannot be tested independently without GUI elements.
- **Improvement Suggestions:** Separate concerns by introducing a model layer that handles data processing and exposes clean interfaces to the view layer.
- **Priority Level:** High

---

### Code Smell Type: Hardcoded Strings
- **Problem Location:** `"產生資料"`, `"分析資料"`, `"顯示資料"`, `"顯示結果"` and `"狀態：尚未開始"`.
- **Detailed Explanation:** These strings are hardcoded and make internationalization or localization challenging.
- **Improvement Suggestions:** Move localized strings into external files or dictionaries for easier translation and maintenance.
- **Priority Level:** Medium

---

### Code Smell Type: Unused Imports / Redundant Dependencies
- **Problem Location:** Importing unused modules (`sys`, `random`, `statistics`).
- **Detailed Explanation:** Although minor, it clutters imports and can confuse developers looking through the file.
- **Improvement Suggestions:** Remove any unused imports to keep the module leaner and cleaner.
- **Priority Level:** Low

---