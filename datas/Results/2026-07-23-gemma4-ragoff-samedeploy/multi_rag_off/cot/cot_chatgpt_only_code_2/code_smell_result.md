- Code Smell Type: Violation of Single Responsibility Principle (God Function)
- Problem Location: `loadAndProcessUsers` function
- Detailed Explanation: This function is doing too many things: handling file I/O, parsing JSON, mapping data to objects, applying business filtering logic, handling logging/debugging, and managing a global cache. This makes the code difficult to test in isolation and hard to maintain. For example, you cannot test the filtering logic without having a physical file on disk.
- Improvement Suggestions: Split the function into smaller, focused functions: `load_users_from_file()`, `parse_user_data()`, and `filter_active_users()`.
- Priority Level: High

- Code Smell Type: Unclear Naming & Inconsistent Style
- Problem Location: `loadAndProcessUsers`, `calculateAverage`, `mainProcess`, and variables like `raw`, `temp`, `r`, `u`.
- Detailed Explanation: The codebase uses `camelCase` for functions, which violates PEP 8 (the standard Python style guide recommending `snake_case`). Furthermore, variable names like `raw`, `temp`, and `r` are non-descriptive, forcing the reader to infer their purpose from the context.
- Improvement Suggestions: Rename functions to `load_and_process_users`, `calculate_average`, etc. Rename variables to be descriptive (e.g., `raw` $\rightarrow$ `user_data_list`, `r` $\rightarrow$ `user_dict`).
- Priority Level: Medium

- Code Smell Type: Fragile Error Handling & Resource Management
- Problem Location: 
  ```python
  f = open(DATA_FILE, "r")
  text = f.read()
  f.close()
  ...
  except:
      raw = []
  ```
- Detailed Explanation: 
  1. Manual `open/close` is risky; if an exception occurs during `read()`, the file handle remains open.
  2. The "bare except" block catches all exceptions (including `KeyboardInterrupt` or `SystemExit`), which can hide critical bugs and make debugging nearly impossible.
- Improvement Suggestions: Use a `with open(...) as f:` context manager for safe file handling. Replace the bare `except:` with `except json.JSONDecodeError:`.
- Priority Level: High

- Code Smell Type: Inconsistent Return Types
- Problem Location: `getTopUser` function
- Detailed Explanation: The function returns three different types depending on the state: a `User` object, a `dict`, or `None`. This forces the caller (`mainProcess`) to use `isinstance` checks to determine how to handle the result, which is a sign of poor API design and increases the likelihood of runtime errors.
- Improvement Suggestions: Ensure the function returns a consistent type. Either always return a `User` object or always return a dictionary.
- Priority Level: Medium

- Code Smell Type: Redundant Logic & Inefficient Operations
- Problem Location: 
  1. `temp = []; for r in raw: temp.append(r)`
  2. `avg = float(str(avg))`
- Detailed Explanation: 
  1. The first block simply copies a list into another list for no apparent reason, wasting memory and CPU.
  2. Converting a float to a string and back to a float is a computationally expensive and illogical way to handle a number.
- Improvement Suggestions: Remove the `temp` list loop entirely and iterate over `raw` directly. Remove the `float(str(avg))` cast.
- Priority Level: Low