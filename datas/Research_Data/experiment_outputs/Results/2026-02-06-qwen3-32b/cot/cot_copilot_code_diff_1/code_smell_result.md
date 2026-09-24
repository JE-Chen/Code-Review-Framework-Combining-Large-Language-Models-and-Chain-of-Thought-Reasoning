### Code Smell Type: Global Variables
**Problem Location**:  
```python
global DATA, RESULTS
```
Used in `generate()`, `analyze()`, and `clear()` functions.

**Detailed Explanation**:  
Global state creates hidden dependencies and violates encapsulation. The mutable `DATA` and `RESULTS` are shared across all requests, causing:
- Data leakage between users (e.g., one user's analysis affects another)
- Thread-safety issues in production (Flask runs multiple threads)
- Complete lack of testability (can't isolate logic without global state)
- Confusion between constant-like naming (`DATA`, `RESULTS` in ALL CAPS) and mutable state

**Improvement Suggestions**:  
Replace global state with a dependency-injected service class:
```python
class AnalysisService:
    def __init__(self):
        self.data = []
        self.results = {}
    
    def generate(self, limit=37):
        self.data = [random.randint(1, 100) for _ in range(limit)]
    
    def analyze(self):
        if not self.data:
            return "No data yet"
        # ... rest of logic using self.data and self.results

# In routes:
service = AnalysisService()

@app.route("/generate")
def generate():
    service.generate()
    return f"Generated {len(service.data)} numbers"

@app.route("/analyze")
def analyze():
    return service.analyze()
```

**Priority Level**: High

---

### Code Smell Type: Duplicate Code
**Problem Location**:  
```python
meanVal = statistics.mean(DATA)
RESULTS["mean"] = meanVal
RESULTS["meanAgain"] = statistics.mean(DATA)  # Duplicate calculation
```

**Detailed Explanation**:  
The same computation (`statistics.mean(DATA)`) is executed twice. This:
- Wastes CPU cycles (though negligible for small data, it's still inefficient)
- Creates maintenance risk (e.g., if mean calculation changes, must update two places)
- Confuses readers (why store identical values under different keys?)
- Indicates poor design (logic duplicated instead of abstracted)

**Improvement Suggestions**:  
Compute once and reuse:
```python
mean_val = statistics.mean(DATA)
RESULTS["mean"] = mean_val
RESULTS["meanAgain"] = mean_val  # If truly needed (but likely redundant)
```
**Better**: Remove `meanAgain` entirely if it serves no purpose.

**Priority Level**: Medium

---

### Code Smell Type: Unclear Naming
**Problem Location**:  
- `meanAgain`, `medianPlus42`
- `DATA` and `RESULTS` (named as constants but mutable)

**Detailed Explanation**:  
Names fail to communicate intent:
- `meanAgain` implies a *recomputation* (it's not)
- `medianPlus42` uses magic number `42` without context
- `DATA`/`RESULTS` violate naming conventions (mutable state in ALL CAPS confuses developers)
- Creates cognitive overhead for maintainers (e.g., "Why 42?")

**Improvement Suggestions**:  
1. Rename redundant keys:  
   ```python
   # Instead of:
   RESULTS["meanAgain"] = statistics.mean(DATA)
   
   # Use:
   RESULTS["mean"] = statistics.mean(DATA)
   ```
2. Replace magic numbers with constants:
   ```python
   MEDIAN_OFFSET = 42  # Add at top of file
   RESULTS["median_plus"] = statistics.median(DATA) + MEDIAN_OFFSET
   ```
3. Rename global state to reflect mutability:
   ```python
   # Replace:
   DATA = []
   RESULTS = {}
   
   # With:
   generated_numbers = []
   analysis_results = {}
   ```

**Priority Level**: Medium

---

### Code Smell Type: Inconsistent State Management
**Problem Location**:  
`analyze()` computes values conditionally (`len(DATA) > 5`/`>10`), but `DATA` is cleared globally.

**Detailed Explanation**:  
State transitions are unclear:
- `/analyze` assumes `DATA` is populated from `/generate`, but no validation
- `RESULTS` accumulates across requests (e.g., `mean` from previous requests lingers)
- No reset logic for `RESULTS` when `DATA` changes (e.g., clearing `RESULTS` on `/generate`)

**Improvement Suggestions**:  
Reset `RESULTS` when `DATA` is modified:
```python
@app.route("/generate")
def generate():
    global DATA, RESULTS
    DATA = [random.randint(1, 100) for _ in range(LIMIT)]
    RESULTS = {}  # Reset analysis results
    return f"Generated {len(DATA)} numbers"
```
**Better**: Use the service class from the first fix to encapsulate state.

**Priority Level**: Low

---

### Code Smell Type: Missing Documentation & Tests
**Problem Location**:  
Entire file lacks docstrings, comments, or tests.

**Detailed Explanation**:  
- No function documentation (e.g., purpose of `/analyze` endpoints)
- No unit tests for core logic (e.g., mean/median calculations)
- Critical for maintainability: New developers cannot understand the codebase.

**Improvement Suggestions**:  
1. Add docstrings:
   ```python
   @app.route("/analyze")
   def analyze():
       """Compute statistics on generated numbers. Returns JSON of results."""
   ```
2. Write unit tests (e.g., using `pytest`):
   ```python
   def test_analyze():
       service = AnalysisService()
       service.data = [10, 20, 30]
       assert service.analyze() == '{"mean": 20.0, ...}'
   ```
3. Add a README explaining endpoints.

**Priority Level**: High