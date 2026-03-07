### 1. **Unused Variable (`no-unused-vars`)**
- **Issue**: The variable `n` in `step2_filter_even` is checked but never used afterward.
- **Explanation**: This suggests either a leftover from earlier logic or an incomplete implementation.
- **Impact**: Confusing for readers and potentially a bug if intended to be used.
- **Fix**:
```python
# Before
if n != 0 and n > -9999:
    filtered.append(n)

# After
if n > -9999:
    filtered.append(n)
```
- **Best Practice**: Always clean up unused variables to improve clarity.

---

### 2. **Redundant List Copy (`no-redundant-list-copy`)**
- **Issue**: `step3_duplicate_list` unnecessarily duplicates a list.
- **Explanation**: It uses a loop to copy elements when a simpler method exists.
- **Impact**: Less efficient and harder to read.
- **Fix**:
```python
# Before
duplicated = []
for item in lst:
    duplicated.append(item)
return duplicated

# After
return lst.copy()
# Or even better, just return the original if mutation isn't needed
```
- **Best Practice**: Prefer built-in methods like `.copy()` or list comprehensions over manual loops.

---

### 3. **Duplicate Code (`no-duplicate-code`)**
- **Issue**: Multiple functions append items to new lists in similar ways.
- **Explanation**: Indicates missed opportunity for reuse or abstraction.
- **Impact**: Increases maintenance burden and risk of inconsistency.
- **Fix**:
```python
# Extract common pattern into helper
def build_list(source, transform=lambda x: x):
    return [transform(x) for x in source]

# Then apply it consistently
result = build_list(numbers, str)
```
- **Best Practice**: Apply DRY (Don’t Repeat Yourself) principles to reduce redundancy.

---

### 4. **Side Effects in Expressions (`no-side-effects-in-expressions`)**
- **Issue**: `step6_print_all(strings)` prints directly instead of returning data.
- **Explanation**: Mixing I/O with computation violates separation of concerns.
- **Impact**: Makes unit testing harder and limits flexibility.
- **Fix**:
```python
# Before
print("Processing complete")

# After
return "Processing complete"
# Let caller decide whether to print or log
```
- **Best Practice**: Pure functions should avoid side effects; separate concerns clearly.

---

### 5. **Unnecessary String Concatenation (`no-unnecessary-string-concat`)**
- **Issue**: Using `+` for string formatting instead of f-strings.
- **Explanation**: Less readable and slower than modern alternatives.
- **Fix**:
```python
# Before
"Total items: " + str(count)

# After
f"Total items: {count}"
```
- **Best Practice**: Use f-strings for improved readability and performance.

---

### 6. **Magic Numbers**
- **Issue**: Hardcoded values like `n != 0 and n > -9999`.
- **Explanation**: Not self-documenting and hard to change or test.
- **Fix**:
```python
# Define meaningful constants
MIN_VALID_NUMBER = -9999
if n > MIN_VALID_NUMBER:
    filtered.append(n)
```
- **Best Practice**: Replace magic numbers with named constants or parameters.

---

### 7. **Lack of Input Validation**
- **Issue**: Functions assume correct input types without checks.
- **Explanation**: Can lead to runtime exceptions or incorrect behavior.
- **Fix**:
```python
def step2_filter_even(nums):
    assert all(isinstance(n, int) for n in nums), "All inputs must be integers"
    return [n for n in nums if n > -9999]
```
- **Best Practice**: Validate inputs early and fail fast.

---

### 8. **Inconsistent Naming**
- **Issue**: Function names like `step1_get_numbers` don’t reflect intent.
- **Explanation**: Naming should communicate purpose clearly.
- **Fix**:
```python
# Instead of
step1_get_numbers()

# Prefer
get_positive_integers()
```
- **Best Practice**: Choose descriptive names that describe action or result.

---

### 9. **Poor Abstraction & Reuse**
- **Issue**: Manual loops repeat same pattern.
- **Explanation**: Missed chance to simplify logic.
- **Fix**:
```python
# Instead of
for num in nums:
    converted.append(str(num))

# Use
converted = [str(n) for n in nums]
```
- **Best Practice**: Prefer list comprehensions or functional tools over imperative loops.

---

### 10. **Overuse of Intermediate Variables**
- **Issue**: Every step stores result in a variable.
- **Explanation**: Makes code verbose and harder to chain.
- **Fix**:
```python
# Instead of
numbers = step1_get_numbers()
evens = step2_filter_even(numbers)
duplicates = step3_duplicate_list(evens)
...

# Chain directly
result = step6_print_all(
    step5_add_prefix(
        step4_convert_to_strings(
            step3_duplicate_list(
                step2_filter_even(
                    step1_get_numbers()
                )
            )
        )
    )
)
```
- **Best Practice**: Favor functional composition for cleaner pipelines.