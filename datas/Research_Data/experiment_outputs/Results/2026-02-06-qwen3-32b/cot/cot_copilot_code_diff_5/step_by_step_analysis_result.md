### 1. `bad-function-name`  
**Issue**: Function name uses camelCase and lacks descriptive meaning.  
**Root Cause**: Poor naming convention choice. Names like `functionThatDoesTooMuchAndIsNotClear` describe *what it isn't* instead of *what it does*.  
**Impact**: Increases cognitive load for readers and hinders code discovery. High risk for maintainability.  
**Fix**: Rename to meaningful snake_case:  
```python
# Before
def functionThatDoesTooMuchAndIsNotClear():
# After
def analyze_sample_data():
```  
**Best Practice**: Follow PEP 8 naming conventions. Names should clearly state *purpose*, not implementation.  

---

### 2. `global-variable`  
**Issue**: Global variable `GLOBAL_DF` creates hidden dependencies.  
**Root Cause**: Using `global` to share state across functions. Violates encapsulation.  
**Impact**: Breaks testability (hard to isolate logic), causes unexpected side effects, and complicates debugging. Critical risk.  
**Fix**: Replace with function parameters/returns:  
```python
# Before
GLOBAL_DF = None
def functionThatDoesTooMuchAndIsNotClear():
    global GLOBAL_DF
# After
def create_sample_dataframe() -> pd.DataFrame:
    return pd.DataFrame(...)
def analyze_data(df: pd.DataFrame) -> None:
    # Use df directly, no globals
```  
**Best Practice**: Eliminate globals. Pass dependencies explicitly (Dependency Injection).  

---

### 3. `bad-constant-name`  
**Issue**: Constant `ANOTHER_GLOBAL` is non-descriptive.  
**Root Cause**: Arbitrary naming without context. "Another" implies redundancy but doesn’t clarify intent.  
**Impact**: Confuses readers; requires mental mapping to understand purpose. Medium risk for readability.  
**Fix**: Rename to meaningful constant:  
```python
# Before
ANOTHER_GLOBAL = "分析開始"
# After
ANALYSIS_START_MESSAGE = "分析開始"
```  
**Best Practice**: Constants should communicate *business intent* (e.g., `MAX_RETRY_ATTEMPTS` not `MAX_VAL`).  

---

### 4. `too-much-in-one-function`  
**Issue**: Function handles data creation, processing, and output.  
**Root Cause**: Violates Single Responsibility Principle (SRP). One function does too many things.  
**Impact**: Long function (25+ lines) is hard to test, debug, and extend. High risk for bugs.  
**Fix**: Split into focused functions:  
```python
def create_sample_data() -> pd.DataFrame: ...
def process_scores(df: pd.DataFrame) -> float: ...
def print_results(mean_age: float) -> None: ...
```  
**Best Practice**: Each function should have *one* reason to change (SRP).  

---

### 5. `broad-exception-catch`  
**Issue**: Catches all exceptions (`Exception`), hiding errors.  
**Root Cause**: Overly generic error handling. The message "我不管錯誤是什麼" ("I don’t care what the error is") shows negligence.  
**Impact**: Masks critical bugs (e.g., `KeyError`), making failures undetectable. High security/quality risk.  
**Fix**: Handle specific exceptions:  
```python
# Before
try:
    ...
except Exception as e:
    print("我不管錯誤是什麼:", e)
# After
try:
    ...
except ValueError as e:
    logging.error("Invalid age data: %s", e)
    raise  # Re-raise for higher-level handling
```  
**Best Practice**: Catch specific exceptions. Log context before re-raising.  

---

### 6. `redundant-condition`  
**Issue**: Nested condition for `mean_age` is redundant.  
**Root Cause**: Unnecessary complexity in logic.  
**Impact**: Reduces readability; increases chance of logic errors. Low risk but wastes effort.  
**Fix**: Simplify to a single range check:  
```python
# Before
if mean_age > 20:
    if mean_age < 50:
# After
if 20 < mean_age < 50:
```  
**Best Practice**: Prefer idiomatic Python over verbose conditionals.  

---

### 7. `missing-docstring`  
**Issue**: Function lacks docstring explaining purpose.  
**Root Cause**: Ignoring documentation as an afterthought.  
**Impact**: Makes codebase harder to onboard and maintain. Low risk but accumulates technical debt.  
**Fix**: Add a concise docstring:  
```python
def analyze_sample_data() -> None:
    """Computes mean age and validates against business rules.
    Prints analysis results to stdout.
    """
```  
**Best Practice**: Document *what* the function does, *why*, and *how* (parameters/return). Use Google/NumPy style.