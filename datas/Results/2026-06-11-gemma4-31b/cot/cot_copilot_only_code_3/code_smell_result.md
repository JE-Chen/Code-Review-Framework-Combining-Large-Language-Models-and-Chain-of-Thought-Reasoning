Here is the professional code review based on the global rules and software engineering standards.

### Code Review Summary
The provided code is functional but suffers from significant "Procedural Over-decomposition." It breaks simple operations into too many tiny, rigid functions, leading to excessive boilerplate and poor maintainability. It also fails to leverage Pythonic idioms, resulting in verbose and inefficient logic.

---

### Detailed Findings

- **Code Smell Type**: Unclear/Poor Naming (Sequential Naming)
- **Problem Location**: `step1_get_numbers`, `step2_filter_even`, `step3_duplicate_list`, etc.
- **Detailed Explanation**: Prefixing functions with `step1_`, `step2_`, etc., is a bad practice. It tightly couples the function names to the current execution order. If a step needs to be moved or inserted, all subsequent functions must be renamed, which is fragile and misleading.
- **Improvement Suggestions**: Use descriptive names based on the function's purpose (e.g., `get_source_numbers`, `filter_even_numbers`, `format_with_prefix`).
- **Priority Level**: High

---

- **Code Smell Type**: Magic Numbers & Redundant Logic
- **Problem Location**: `if n % 2 == 0 and n != 0 and n > -9999:` in `step2_filter_even`
- **Detailed Explanation**: The value `-9999` is a "magic number" with no explained context. Furthermore, `n != 0` is redundant if the goal is to filter even numbers (since 0 is even, this is a specific business rule that should be documented). The logic is cluttered and lacks semantic clarity.
- **Improvement Suggestions**: Extract `-9999` into a named constant (e.g., `MIN_VALID_THRESHOLD`). Add a comment explaining why 0 is excluded.
- **Priority Level**: Medium

---

- **Code Smell Type**: Over-decomposition / Excessive Boilerplate
- **Problem Location**: `step3_duplicate_list`, `step4_convert_to_strings`, `step5_add_prefix`
- **Detailed Explanation**: These functions are "trivial wrappers." They each contain a simple loop to perform a basic transformation. This leads to "fragmented logic" where the reader must jump between five different functions to understand a single data pipeline, increasing cognitive load.
- **Improvement Suggestions**: Consolidate these transformations. Use list comprehensions or a mapping function to handle simple transformations in a more concise and Pythonic way.
- **Priority Level**: Medium

---

- **Code Smell Type**: Deeply Nested Conditionals (Arrow Anti-pattern)
- **Problem Location**: `step6_print_all`
- **Detailed Explanation**: The function uses nested `if/else` blocks. While small here, this pattern leads to "Arrow Code" that becomes unreadable as complexity grows. The check `if len(s) > 0` is also a non-Pythonic way to check for empty strings.
- **Improvement Suggestions**: Use "Guard Clauses" to return or continue early. Use `if not s:` to check for empty strings.
- **Priority Level**: Low

---

- **Code Smell Type**: Reinventing the Wheel / Inefficiency
- **Problem Location**: `step7_redundant_summary`
- **Detailed Explanation**: The function manually iterates through a list to count items. Python provides a built-in `len()` function that is implemented in C and is significantly faster and more readable.
- **Improvement Suggestions**: Replace the entire loop with `return f"Total items: {len(strings)}"` using an f-string.
- **Priority Level**: Medium

---

- **Code Smell Type**: Lack of Type Hinting & Documentation
- **Problem Location**: All function signatures.
- **Detailed Explanation**: There are no type hints or docstrings. In a professional codebase, it is unclear what `nums` or `strings` are expected to be (Lists? Generators? Sets?), making the code harder to test and maintain.
- **Improvement Suggestions**: Add PEP 484 type hints (e.g., `nums: list[int]`) and brief docstrings explaining the intent of each transformation.
- **Priority Level**: Medium

---

### Final Refactoring Recommendation (Example)

To adhere to the global rules of **Readability**, **Software Engineering Standards**, and **Logic & Correctness**, the code should be refactored as follows:

```python
from typing import List

MIN_VALID_THRESHOLD = -9999

def get_numbers() -> List[int]:
    return [1, 2, 3, 4, 5, 6, 7, 8, 9]

def process_numbers(nums: List[int]) -> List[str]:
    # Consolidate trivial steps into a clean pipeline
    # Filter: Even, non-zero, and above threshold
    filtered = [n for n in nums if n % 2 == 0 and n != 0 and n > MIN_VALID_THRESHOLD]
    
    # Transform: Duplicate, Convert to string, and Prefix
    processed = []
    for n in filtered:
        val = f"VAL_{n}"
        processed.extend([val, val]) 
    return processed

def print_results(strings: List[str]) -> None:
    for s in strings:
        if not s:
            print("Empty string found")
            continue
        
        if s.startswith("VAL"):
            print(f"Output: {s}")
        else:
            print(f"Ignored: {s}")

def main():
    nums = get_numbers()
    processed_strings = process_numbers(nums)
    print_results(processed_strings)
    print(f"Total items: {len(processed_strings)}")

if __name__ == "__main__":
    main()
```