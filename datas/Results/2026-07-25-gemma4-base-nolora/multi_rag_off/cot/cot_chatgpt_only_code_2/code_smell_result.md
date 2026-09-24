- Code Smell Type: Violation of Single Responsibility Principle (SRP) / Long Function
- Problem Location: `loadAndProcessUsers` function
- Detailed Explanation: This function is doing too many things: handling file I/O, parsing JSON, transforming raw data into objects, applying business filtering logic, and managing a global cache. This makes the code difficult to test in isolation (e.g., you cannot test the filtering logic without a physical file) and hard to maintain.
- Improvement Suggestions: Split the function into three distinct parts: 
    1. A data access function to read the file and return raw JSON.
    2. A factory function to convert raw dictionaries into `User` objects.
    3. A filter function to apply the business rules (age, score, active status).
- Priority Level: High

- Code Smell Type: Unclear Naming & Poor Readability
- Problem Location: `loadAndProcessUsers` (variables `flag`, `raw`, `temp`, `r`, `u`)
- Detailed Explanation: Variable names like `flag`, `raw`, and `temp` are non-descriptive. `flag` is particularly problematic as it doesn't indicate what it controls (forcing users to be active). `temp` is used to copy a list for no apparent reason, adding unnecessary cognitive load and memory overhead.
- Improvement Suggestions: Rename `flag` to `force_active`, `raw` to `user_data`, and `u` to `user`. Remove the `temp` list entirely and iterate directly over the parsed JSON.
- Priority Level: Medium

- Code Smell Type: Inconsistent Return Types
- Problem Location: `getTopUser` function
- Detailed Explanation: The function returns three different types depending on the state: a `User` object, a `dict`, or `None`. This forces the caller (`mainProcess`) to use `isinstance` checks to determine how to handle the result, which is a sign of poor API design and increases the risk of `TypeError` or `KeyError` during future modifications.
- Improvement Suggestions: Ensure the function always returns a consistent type. Either always return a `User` object or always return a dictionary. The logic regarding `best.score > 90` should be handled by the formatter/caller, not the retrieval logic.
- Priority Level: High

- Code Smell Type: Fragile Resource Management & Error Handling
- Problem Location: `loadAndProcessUsers` (file opening and `try-except` block)
- Detailed Explanation: 
    1. The file is opened using `f = open()` and closed manually. If `json.loads()` raises an exception, `f.close()` is never called, leading to a potential memory leak/file lock.
    2. The `except:` block is a "bare except," which catches all exceptions (including `KeyboardInterrupt` or `SystemExit`), masking potential bugs.
- Improvement Suggestions: Use the `with open(...) as f:` context manager to ensure the file is closed automatically. Replace the bare `except:` with `except json.JSONDecodeError:`.
- Priority Level: Medium

- Code Smell Type: Redundant Logic / Performance Bottleneck
- Problem Location: `calculateAverage` function
- Detailed Explanation: The function manually iterates to count and sum, which is redundant in Python. Furthermore, the line `avg = float(str(avg))` is highly inefficient and logically unnecessary, as the result of a division in Python 3 is already a float.
- Improvement Suggestions: Use built-in functions: `return sum(u.score for u in users) / len(users) if users else 0`. Remove the `float(str())` conversion.
- Priority Level: Low