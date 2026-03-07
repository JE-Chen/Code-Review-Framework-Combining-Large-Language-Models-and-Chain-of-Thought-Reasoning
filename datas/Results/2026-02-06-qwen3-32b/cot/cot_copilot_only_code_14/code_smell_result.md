### Code Smell Type: Global Variables
**Problem Location**:  
```python
dataFrameLike = []
resultCache = {}
textOutput = None
tableWidget = None
labelStatus = None
```

**Detailed Explanation**:  
Extensive global state violates encapsulation and makes code non-testable. Functions (`generateData`, `analyzeData`, etc.) rely on global variables, causing hidden dependencies and unintended side effects. For example, `analyzeData` mutates `resultCache` without explicit context, making it impossible to reason about behavior in isolation. This also prevents parallel execution or reuse of functions.

**Improvement Suggestions**:  
Replace global variables with dependency injection. Create a dedicated `AnalysisManager` class to encapsulate state and logic. Pass UI components as arguments to functions instead of relying on globals. Example:
```python
class AnalysisManager:
    def __init__(self, table_widget, text_edit, label):
        self.data = []
        self.result_cache = {}
        self.table_widget = table_widget
        self.text_edit = text_edit
        self.label = label

    def generate_data(self):
        self.data = [[random.randint(1, 100), random.random() * 50, random.choice(["A", "B", "C"])] for _ in range(37)]
    
    def analyze(self):
        # ... (logic without global access)
```

**Priority Level**: High  

---

### Code Smell Type: Violation of Single Responsibility Principle
**Problem Location**:  
```python
def analyzeData():
    global dataFrameLike, resultCache
    if len(dataFrameLike) > 0:
        nums = [row[0] for row in dataFrameLike]
        vals = [row[1] for row in dataFrameLike]
        cats = [row[2] for row in dataFrameLike]
        if len(nums) > 5:
            meanNum = statistics.mean(nums)
            resultCache["meanNum"] = meanNum
            resultCache["meanNumAgain"] = statistics.mean(nums)  # Redundant
            if meanNum > 50:
                resultCache["flag"] = "HIGH"
            else:
                resultCache["flag"] = "LOW"
        if len(vals) > 10:
            resultCache["medianVal"] = statistics.median(vals)
            resultCache["medianValPlus42"] = statistics.median(vals) + 42
        resultCache["catCount"] = {c: cats.count(c) for c in set(cats)}
    else:
        resultCache["error"] = "No data"
```

**Detailed Explanation**:  
This function handles data extraction, statistical computation, result caching, and error handling. It should be split into focused units:  
1. Data extraction → `extract_numerical_values`  
2. Statistical analysis → `compute_statistics`  
3. Result caching → `update_result_cache`  
Violating SRP makes the function hard to test, debug, and extend (e.g., adding new statistics requires modifying this monolithic function).

**Improvement Suggestions**:  
Refactor into separate functions/classes. Example:
```python
def compute_statistics(data):
    if not data:
        return {"error": "No data"}
    
    nums = [row[0] for row in data]
    vals = [row[1] for row in data]
    cats = [row[2] for row in data]
    
    stats = {}
    if len(nums) > 5:
        mean = statistics.mean(nums)
        stats["meanNum"] = mean
        stats["flag"] = "HIGH" if mean > 50 else "LOW"
    
    if len(vals) > 10:
        median = statistics.median(vals)
        stats["medianVal"] = median
        stats["medianValPlus42"] = median + 42
    
    stats["catCount"] = {c: cats.count(c) for c in set(cats)}
    return stats
```

**Priority Level**: High  

---

### Code Smell Type: Unnecessary Redundancy
**Problem Location**:  
```python
meanNum = statistics.mean(nums)
resultCache["meanNum"] = meanNum
resultCache["meanNumAgain"] = statistics.mean(nums)  # Computed twice
```

**Detailed Explanation**:  
The same mean value is computed twice for `meanNum` and `meanNumAgain`. This wastes CPU cycles and confuses maintainers. The second entry (`meanNumAgain`) serves no purpose and likely indicates a mistake in design. Redundant operations are a classic code smell.

**Improvement Suggestions**:  
Replace the redundant line with:
```python
resultCache["meanNumAgain"] = meanNum  # Use existing computed value
```
Or remove the key entirely if unused.

**Priority Level**: Medium  

---

### Code Smell Type: Magic Numbers
**Problem Location**:  
```python
generateData():
    [[random.randint(1, 100), random.random() * 50, ...]]
analyzeData():
    if len(nums) > 5:  # Magic number
    if len(vals) > 10: # Magic number
```

**Detailed Explanation**:  
Hardcoded values (e.g., `5`, `10`, `100`, `50`) lack context. Why `5` for mean computation? Why `100` for random numbers? This hurts maintainability. If requirements change (e.g., `5` → `10`), the code must be manually scanned for all magic numbers.

**Improvement Suggestions**:  
Define constants with descriptive names:
```python
MIN_DATA_POINTS_FOR_MEAN = 5
MIN_DATA_POINTS_FOR_MEDIAN = 10
MAX_RANDOM_VALUE = 100
MAX_RANDOM_FLOAT = 50.0
```
Use these constants in place of raw numbers.

**Priority Level**: Low  

---

### Code Smell Type: Tight Coupling with UI Components
**Problem Location**:  
```python
def showData():
    global tableWidget, dataFrameLike
    tableWidget.setRowCount(len(dataFrameLike))
    # ... (UI-specific logic)

def showResults():
    global textOutput, resultCache
    textOutput.clear()
    # ... (UI-specific logic)
```

**Detailed Explanation**:  
UI logic is entangled with business logic. Functions like `showData` and `showResults` directly manipulate UI elements (`tableWidget`, `textOutput`) instead of returning data. This prevents testing without a GUI and forces all logic to be tied to Qt.

**Improvement Suggestions**:  
Separate data processing from UI presentation. Return computed data from `analyzeData`, then let the UI layer render it:
```python
# In main:
def on_analysis_complete(stats):
    show_results_in_ui(textOutput, stats)
    update_status(labelStatus, "分析完成！")

# AnalysisManager's analyze method returns stats
```

**Priority Level**: High