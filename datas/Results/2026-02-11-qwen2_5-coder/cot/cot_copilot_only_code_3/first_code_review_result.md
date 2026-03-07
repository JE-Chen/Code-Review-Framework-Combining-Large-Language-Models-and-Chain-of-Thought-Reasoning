```diff
- **Indentation**: The code uses tabs for indentation, which can cause inconsistencies. It is recommended to use spaces for indentation.
- **Comments**: There are no comments explaining what each function does. Adding comments would improve understanding.
- **Variable Naming**: Variable names like `nums`, `duplicated`, `str_list`, etc., are generic and do not provide clear information about their purpose.
- **Function Names**: Function names like `step1_get_numbers`, `step2_filter_even`, etc., suggest they are part of a larger process but lack context.
- **Modularization**: Each function performs a single task, which is good, but the functions could benefit from more descriptive names that reflect their purpose.
- **Redundant Summary**: The `step7_redundant_summary` function counts the number of items in the list, which is redundant since Python has built-in functions like `len()`.
- **Main Function**: The `main` function orchestrates the workflow, but it could be split into smaller functions to improve modularity.
- **Print Statements**: The `step6_print_all` function prints messages based on certain conditions, which could be encapsulated in a separate utility function.
```

### Suggested Improvements

```python
def get_numbers():
    return [1, 2, 3, 4, 5, 6, 7, 8, 9]

def filter_even_numbers(numbers):
    return [n for n in numbers if n % 2 == 0 and n != 0 and n > -9999]

def duplicate_list(numbers):
    return [n for n in numbers for _ in range(2)]

def convert_numbers_to_strings(numbers):
    return [str(n) for n in numbers]

def add_prefix_to_strings(strings):
    return ["VAL_" + s for s in strings]

def print_filtered_strings(strings):
    for s in strings:
        if len(s) > 0 and s.startswith("VAL"):
            print(f"Output: {s}")
        elif len(s) > 0:
            print(f"Ignored: {s}")

def summarize_items(strings):
    return f"Total items: {len(strings)}"

def main():
    numbers = get_numbers()
    even_numbers = filter_even_numbers(numbers)
    duplicated_numbers = duplicate_list(even_numbers)
    string_list = convert_numbers_to_strings(duplicated_numbers)
    prefixed_strings = add_prefix_to_strings(string_list)
    print_filtered_strings(prefixed_strings)
    summary = summarize_items(prefixed_strings)
    print(summary)

if __name__ == "__main__":
    main()
```

This refactored version improves readability, adheres to naming conventions, and enhances modularity.