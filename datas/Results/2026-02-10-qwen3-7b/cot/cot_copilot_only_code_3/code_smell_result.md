### Code Smell Type:
1. **Long Function**  
2. **Magic Numbers**  
3. **Redundant Code**  
4. **Tight Coupling**  
5. **Duplicate Code**  

---

### Problem Location & Detailed Explanation:

#### 1. **Long Function**  
- **Location**: `step2_filter_even`, `step6_print_all`, `step7_redundant_summary`  
- **Explanation**: Functions like `step2_filter_even` have complex logic and multiple conditions, reducing readability and maintainability.  
- **Impact**: Hard to understand and test, increasing the risk of bugs.  

#### 2. **Magic Numbers**  
- **Location**: `step2_filter_even`  
- **Explanation**: The condition `n > -9999` is a hardcoded value with no clear rationale.  
- **Impact**: Makes the code brittle and hard to maintain.  

#### 3. **Redundant Code**  
- **Location**: `step7_redundant_summary`  
- **Explanation**: The function returns the same count as a loop, which is redundant.  
- **Impact**: Increases boilerplate code and reduces clarity.  

#### 4. **Tight Coupling**  
- **Location**: `main()` function  
- **Explanation**: The main function calls all steps, creating a monolithic structure.  
- **Impact**: Difficult to test and refactor.  

#### 5. **Duplicate Code**  
- **Location**: `step3_duplicate_list`  
- **Explanation**: The duplicated list is the same as the original list.  
- **Impact**: Redundant code and potential errors.  

---

### Improvement Suggestions:

1. **Long Function**:  
   - Split into smaller, focused functions (e.g., `filter_even`, `duplicate_list`, `print_all`).  
   - Example: `step2_filter_even` → `filter_even` with simplified logic.  

2. **Magic Numbers**:  
   - Replace `n > -9999` with a constant (e.g., `MIN_VALUE = -9999`).  

3. **Redundant Code**:  
   - Remove `step7_redundant_summary` and calculate count in `main()`.  

4. **Tight Coupling**:  
   - Encapsulate steps into a pipeline or use a class.  

5. **Duplicate Code**:  
   - Use a helper function to duplicate elements.  

---

### Priority Level:
- **High**: Long Function, Magic Numbers, Redundant Code  
- **Medium**: Tight Coupling, Duplicate Code  
- **Low**: Long Function (repeated)