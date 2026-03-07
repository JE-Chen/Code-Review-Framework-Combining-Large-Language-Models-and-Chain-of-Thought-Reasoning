### 1. **Mutable Default Arguments**  
**Issue:** Mutable default arguments (`y=[]`, `z={"a": 1}`) cause unexpected state sharing across function calls.  
**Root Cause:** Python evaluates default arguments *once* at definition time, so all calls share the same mutable object.  
**Impact:** Critical bug risk (e.g., appending to `y` in one call affects all subsequent calls). Violates purity and predictability.  
**Suggested Fix:**  
```python
def do_everything_and_nothing_at_once(x=None, y=None, z=None):
    y = y or []
    z = z or {"a": 1}
```  
**Best Practice:** *Never use mutable types (list, dict, set) as default arguments.*  

---

### 2. **Unused Parameter `y`**  
**Issue:** Parameter `y` is declared but never used.  
**Root Cause:** Redundant parameter due to poor design or copy-paste errors.  
**Impact:** Confuses callers, increases cognitive load, and signals poor code hygiene.  
**Suggested Fix:**  
```python
# Remove unused parameter `y` entirely
def do_everything_and_nothing_at_once(x=None, z=None):
```  
**Best Practice:** *Parameters should always serve a purpose. Remove unused ones.*  

---

### 3. **Unused Parameter `z`**  
**Issue:** Parameter `z` is declared but never used.  
**Root Cause:** Same as above—unnecessary complexity in the interface.  
**Impact:** Same as unused `y` (confusion, maintenance burden).  
**Suggested Fix:**  
```python
# Remove unused parameter `z`
def do_everything_and_nothing_at_once(x=None):
```  
**Best Practice:** *Keep function signatures minimal and intentional.*  

---

### 4. **Missing Docstring**  
**Issue:** Function lacks documentation explaining purpose, parameters, and return values.  
**Root Cause:** Overlooked documentation step during implementation.  
**Impact:** Hinders readability, maintainability, and onboarding. Makes code "black box."  
**Suggested Fix:**  
```python
def do_everything_and_nothing_at_once(x=None):
    """Generate and analyze data, return summary metrics.
    
    Args:
        x: Input value (int). Optional.
    
    Returns:
        dict: Summary metrics (mean, std, max, min).
    """
```  
**Best Practice:** *Document all public functions with docstrings.*  

---

### 5. **Violation of Single Responsibility Principle**  
**Issue:** Function handles data generation, analysis, plotting, and side effects.  
**Root Cause:** Overloaded function with multiple unrelated responsibilities.  
**Impact:** Impossible to test/reuse; high coupling; prone to bugs.  
**Suggested Fix:** Split into focused functions:  
```python
def generate_data(x): ...  # Data generation
def analyze_dataframe(df): ...  # Analysis
def plot_analysis(df): ...  # Side effect (plotting)
```  
**Best Practice:** *One function = one clear responsibility.*  

---

### 6. **Side Effects (Plotting + Global Mutation)**  
**Issue:** Function modifies global state (`GLOBAL_THING`) and triggers UI (`plt.show()`).  
**Root Cause:** Mixing core logic with I/O and state mutation.  
**Impact:** Breaks testability (requires mocks), introduces hidden dependencies, and complicates execution.  
**Suggested Fix:**  
```python
# Move side effects to dedicated functions
def plot_analysis(df):
    plt.figure()
    # ... plotting code ...
    plt.show()

def main():
    df = generate_data(x)
    result = analyze_dataframe(df)
    plot_analysis(df)  # Caller controls side effects
```  
**Best Practice:** *Avoid side effects in core logic; separate concerns.*  

---

### 7. **Magic Number `37`**  
**Issue:** Unexplained number `37` used without context.  
**Root Cause:** Hardcoded value without semantic meaning.  
**Impact:** Reduces readability; requires guesswork to understand.  
**Suggested Fix:**  
```python
# Replace with descriptive constant
MATH_CONSTANT = 37  # Used in sqrt adjustment per spec v2.1

# Usage:
value = math.sqrt(value) * MATH_CONSTANT
```  
**Best Practice:** *Replace magic numbers with named constants.*  

---

### 8. **Global Mutable State (`GLOBAL_THING`)**  
**Issue:** Modifying module-level global `GLOBAL_THING` creates hidden coupling.  
**Root Cause:** Relying on global state instead of explicit parameters/return values.  
**Impact:** Makes code non-deterministic, hard to test, and prone to race conditions.  
**Suggested Fix:**  
```python
# Remove global; return state explicitly
def do_everything_and_nothing_at_once(x=None):
    # ... compute result ...
    return df, analysis_result  # Caller manages state
```  
**Best Practice:** *Prefer explicit parameters over global state.*  

---

### 9. **Global Cache (`STRANGE_CACHE`)**  
**Issue:** Module-level cache `STRANGE_CACHE` mutates state across calls.  
**Root Cause:** Uncontrolled global cache with no clear ownership.  
**Impact:** Breaks referential transparency; causes subtle bugs.  
**Suggested Fix:**  
```python
# Replace with cache passed via function parameters
def analyze_dataframe(df, cache=None):
    cache = cache or {}  # Avoid mutating module-level state
    # ... use cache ...
```  
**Best Practice:** *State should be encapsulated within functions or objects.*  

---

### 10. **Inefficient Loop (`iloc`)**  
**Issue:** Loop over DataFrame using `iloc` (slow O(n) vs. vectorized O(1)).  
**Root Cause:** Ignoring Pandas’ vectorized operations.  
**Impact:** Significant performance degradation (especially for large DataFrames).  
**Suggested Fix:**  
```python
# Replace loop with vectorized operations
weird_sum = df.apply(
    lambda row: row["mystery"] if row["mystery"] > 0 else abs(row["col_three"]),
    axis=1
).sum()
```  
**Best Practice:** *Use vectorized operations instead of loops with `iloc`.*  

---

### 11. **Broad Exception Handling (`except:`)**  
**Issue:** Catching `Exception` silently ignores errors (e.g., `except:`).  
**Root Cause:** Overly broad exception handling to avoid crashes.  
**Impact:** Masks bugs, prevents debugging, and hides failures.  
**Suggested Fix:**  
```python
# Replace with specific handling or remove try/except
if isinstance(value, (int, float)):
    value = float(value)
else:
    raise ValueError("Invalid value type")  # Fail fast
```  
**Best Practice:** *Catch specific exceptions or handle errors explicitly.*  

---

### 12. **Unnecessary Sleep**  
**Issue:** `time.sleep(0.01)` adds unexplained delay.  
**Root Cause:** Assumed "need" for timing (e.g., to avoid race conditions).  
**Impact:** Slows execution without benefit; reduces test speed.  
**Suggested Fix:**  
```python
# Remove sleep entirely
# No justification for delay in core logic
```  
**Best Practice:** *Avoid sleep calls in business logic; use explicit synchronization if needed.*  

---

### Summary of Critical Fixes  
| **Issue**                          | **Priority** | **Key Fix**                                  |
|------------------------------------|--------------|---------------------------------------------|
| Mutable defaults + unused params   | High         | Replace defaults with `None`, remove unused args |
| Global state (`GLOBAL_THING`, `STRANGE_CACHE`) | High | Return state explicitly; remove globals     |
| Single responsibility violation      | High         | Split function into focused units           |
| Magic number `37`                  | Medium       | Replace with `MATH_CONSTANT`                |
| Broad exception handling           | Medium       | Catch specific exceptions or remove try/except |
| Inefficient loop                   | Medium       | Use vectorized operations                   |
| Unnecessary sleep                  | Low          | Remove `time.sleep` calls                   |