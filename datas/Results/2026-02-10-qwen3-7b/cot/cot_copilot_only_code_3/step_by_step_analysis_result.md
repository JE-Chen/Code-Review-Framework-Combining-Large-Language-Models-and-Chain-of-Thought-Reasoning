### **Code Smell Review & Analysis**

---

#### **1. Long Function**  
- **Issue**: `step2_filter_even` contains complex logic and multiple conditions.  
- **Impact**: Hard to understand and test.  
- **Root Cause**: Single function handles too many responsibilities.  
- **Fix**: Split into smaller, focused functions (e.g., `filter_even`, `duplicate_list`).  
- **Example**:  
  ```python
  def filter_even(numbers):
      return [n for n in numbers if n % 2 == 0]
  ```

---

#### **2. Magic Numbers**  
- **Issue**: `n > -9999` is hardcoded with no rationale.  
- **Impact**: Brittleness and lack of clarity.  
- **Root Cause**: No documentation for thresholds.  
- **Fix**: Use a constant and explain its purpose.  
- **Example**:  
  ```python
  MIN_VALUE = -9999
  if n > MIN_VALUE:
      ...
  ```

---

#### **3. Redundant Code**  
- **Issue**: `step7_redundant_summary` returns the same count as a loop.  
- **Impact**: Boilerplate and reduced clarity.  
- **Root Cause**: Duplicate logic.  
- **Fix**: Calculate count in `main()`.  
- **Example**:  
  ```python
  def main():
      count = len(data)
      print(f"Total elements: {count}")
  ```

---

#### **4. Tight Coupling**  
- **Issue**: `main()` calls all steps in a monolithic structure.  
- **Impact**: Hard to test and refactor.  
- **Root Cause**: No encapsulation.  
- **Fix**: Encapsulate steps into a pipeline or class.  
- **Example**:  
  ```python
  class DataPipeline:
      def __init__(self):
          self.steps = [filter_even, duplicate_list, print_all]
      def run(self, data):
          for step in self.steps:
              step(data)
  ```

---

#### **5. Duplicate Code**  
- **Issue**: `step3_duplicate_list` is the same as the original.  
- **Impact**: Redundancy and potential errors.  
- **Root Cause**: No helper function.  
- **Fix**: Use a helper function.  
- **Example**:  
  ```python
  def duplicate_list(lst):
      return [item for item in lst for _ in range(2)]
  ```

---

### **Priority Level**  
- **High**: Long Function, Magic Numbers, Redundant Code  
- **Medium**: Tight Coupling, Duplicate Code  

---

### **Best Practice Notes**  
1. **DRY Principle**: Avoid duplication by reusing logic.  
2. **SOLID**: Encapsulate responsibilities into small, focused functions.  
3. **Naming Conventions**: Use clear, descriptive names for variables and functions.