### Diff #1

#### Summary
This PR introduces several utility functions that process lists of numbers and strings, demonstrating common list manipulation techniques. The functions include filtering even numbers, duplicating lists, converting to strings, adding prefixes, printing based on conditions, and summarizing counts.

#### Linting Issues
- **PEP 8 Compliance**: Some lines exceed the recommended maximum length of 79 characters.
  - Example: Line 23 in `step6_print_all`

- **Redundant Assignment**: The variable `count` in `step7_redundant_summary` is assigned but never used elsewhere.
  - Example: Line 31 in `step7_redundant_summary`

- **Implicit String Concatenation**: String concatenation in `step7_redundant_summary` can be improved for clarity.
  - Example: Line 31 in `step7_redundant_summary`

#### Code Smells
- **Side Effects in Utility Functions**: Many functions have side effects like printing, which should be avoided in pure functions.
  - Example: `step6_print_all`

- **Redundant Operations**: Function `step7_redundant_summary` counts elements without storing them, leading to unnecessary computation.
  - Example: `step7_redundant_summary`

- **Lack of Documentation**: Functions lack docstrings explaining their purpose and parameters.
  - Example: All functions

Recommendations:
- Refactor functions to avoid side effects.
- Add docstrings for better understanding.
- Simplify operations where possible.

### Diff #2

#### Summary
This PR contains a single function that demonstrates the use of list comprehensions and generator expressions for various operations.

#### Linting Issues
- **PEP 8 Compliance**: Lines exceed the recommended maximum length of 79 characters.
  - Example: Line 15 in `process_data`

#### Code Smells
- **Use of List Comprehensions for Side Effects**: List comprehensions are used for operations that could benefit from generators.
  - Example: `filtered_nums` in `process_data`

- **Redundant Operations**: The final operation to convert all elements to uppercase is redundant if they were already in that format.
  - Example: `uppercased_nums` in `process_data`

Recommendations:
- Use generators for side-effect-free operations.
- Remove redundant transformations.