### 🧪 Code Smell Review & Linter Message Analysis

---

#### **1. Linter Message 1**  
**Issue**: `filter_high_scores()` condition `s > 40` is incorrect (threshold is 50).  
**Root Cause**: Logic error in condition handling.  
**Impact**: Incorrect filtering leads to wrong results.  
**Fix**: Update condition to `s > 50`.  
**Best Practice**: Use constants for thresholds.  

---

#### **2. Linter Message 2**  
**Issue**: `process_misc()` has redundant logic.  
**Root Cause**: Ambiguous conditions and duplicated code.  
**Impact**: Harder to maintain and test.  
**Fix**: Extract common logic into helper methods.  
**Best Practice**: Extract repeated patterns.  

---

#### **3. Linter Message 3**  
**Issue**: Functions lack docstrings.  
**Root Cause**: Lack of documentation.  
**Impact**: Poor understanding of function purpose.  
**Fix**: Add docstrings with parameters and return values.  
**Best Practice**: Write clear, concise docstrings.  

---

### ⚠️ Key Code Smell Categories & Fixes

---

#### **1. Long Function**  
- **Problem**: `calculate_average_scores()` and `filter_high_scores()` are too complex.  
- **Fix**: Split into smaller, focused functions.  
- **Example**:  
  ```python
  def calculate_average_scores(scores):
      return sum(scores) / len(scores)
  
  def filter_high_scores(scores):
      return [s for s in scores if s > 50]
  ```

---

#### **2. Magic Numbers**  
- **Problem**: Threshold `50` hardcoded.  
- **Fix**: Define in constants or config.  
- **Example**:  
  ```python
  MIN_THRESHOLD = 50
  ```

---

#### **3. Duplicate Code**  
- **Problem**: `main()` and `process_misc()` share logic.  
- **Fix**: Extract common logic into a helper function.  
- **Example**:  
  ```python
  def process_data(scores):
      return calculate_average(scores), filter_high_scores(scores)
  ```

---

### 💡 Best Practices Summary  
1. **SOLID Principle**: Single Responsibility, Open/Closed.  
2. **DRY**: Avoid repetition.  
3. **Naming**: Use descriptive names.  
4. **Documentation**: Add docstrings.  

---

### 📌 Final Recommendation  
Refactor core functions, extract helpers, and add docstrings.