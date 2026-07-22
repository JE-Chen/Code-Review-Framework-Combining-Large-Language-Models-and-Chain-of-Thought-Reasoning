- Code Smell Type: Violation of Single Responsibility Principle (SRP) / Long Function
- Problem Location: `loadAndProcessUsers` function
- Detailed Explanation: This function is doing too many things: handling file I/O, parsing JSON, transforming raw data into objects, applying business filtering logic, and managing a global cache. This makes the code difficult to test in isolation and hard to maintain. For example, you cannot test the filtering logic without having a physical file on disk.
- Improvement Suggestions: Split the function into smaller, dedicated functions: `load_users_from_file()`, `parse_user_data()`, and `filter_active_users()`.
- Priority Level: High

- Code Smell Type: Unclear Naming & Inconsistent Conventions
- Problem Location: `loadAndProcessUsers`, `calculateAverage`, `mainProcess`, `flag`, `r`, `temp`
- Detailed Explanation: The codebase uses `camelCase` for functions, which violates PEP 8 (the standard Python style guide that prescribes `snake_case`). Additionally, variables like `flag`, `r`, and `temp` are non-descriptive, making it unclear what the "flag" actually controls or what "temp" represents.
- Improvement Suggestions: Rename functions to `load_and_process_users`, `calculate_average`, etc. Rename `flag` to something descriptive like `force_active` and `r` to `user_data`.
- Priority Level: Medium

- Code Smell Type: Fragile Error Handling & Resource Management
- Problem Location: 
  1. `f = open(DATA_FILE, "r") ... f.close()`
  2. `except: raw = []`
- Detailed Explanation: 
  1. Opening files without a `with` statement is risky; if an exception occurs during `f.read()`, the file handle remains open.
  2. The "bare except" block catches every possible exception (including KeyboardInterrupt), which hides bugs and makes debugging nearly impossible.
- Improvement Suggestions: Use `with open(DATA_FILE, "r") as f:`. Replace the bare `except:` with `except json.JSONDecodeError:`.
- Priority Level: High

- Code Smell Type: Inconsistent Return Types
- Problem Location: `getTopUser`
- Detailed Explanation: The function returns three different types depending on the state: a `User` object, a `dict`, or `None`. This forces the caller (`mainProcess`) to use `isinstance` checks to determine how to handle the result, which increases complexity and the likelihood of runtime errors.
- Improvement Suggestions: Ensure the function returns a consistent type (always a `User` object or `None`). Formatting the output as a dictionary should be the responsibility of a separate formatting function, not the retrieval logic.
- Priority Level: Medium

- Code Smell Type: Redundant Logic / Inefficient Code
- Problem Location: 
  1. `temp = []; for r in raw: temp.append(r)`
  2. `avg = float(str(avg))`
- Detailed Explanation: 
  1. The loop to copy `raw` into `temp` is entirely redundant as it creates a shallow copy of the list for no apparent reason.
  2. Converting a float to a string and back to a float is a "no-op" that wastes CPU cycles and reduces readability.
- Improvement Suggestions: Remove the `temp` list loop and the `float(str(avg))` conversion.
- Priority Level: Low