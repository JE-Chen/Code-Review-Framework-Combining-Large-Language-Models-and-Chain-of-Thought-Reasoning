- Code Smell Type: Magic Numbers (Sentinel Values)
- Problem Location: `risky_division` (returns `9999`, `-1`), `convert_to_int` (returns `0`, `-999`), `read_file` (returns `"FILE_NOT_FOUND"`)
- Detailed Explanation: The functions use arbitrary numbers or strings to signal errors instead of raising exceptions or returning a structured result (like `None` or a Result object). This forces the caller to know exactly which magic number corresponds to which error, leading to fragile code. For example, if `9999` is a valid result of a division, the caller cannot distinguish between a successful calculation and a `ZeroDivisionError`.
- Improvement Suggestions: Raise specific custom exceptions or return `None` if the value is missing. Let the calling function decide how to handle the failure.
- Priority Level: High

- Code Smell Type: Overly Broad Exception Handling (Pokemon Exception Handling)
- Problem Location: `except Exception as e:` in almost every function, and nested `try...except Exception` in `process_data`.
- Detailed Explanation: Catching the base `Exception` class hides unexpected bugs (like `KeyboardInterrupt`, `MemoryError`, or `NameError`) that should typically crash the program during development. In `process_data`, the nested broad catches make it nearly impossible to debug why a specific piece of data failed to process.
- Improvement Suggestions: Catch only the specific exceptions you expect (e.g., `ValueError`, `IOError`). Remove the outer `try...except Exception` blocks that serve no purpose other than silencing errors.
- Priority Level: High

- Code Smell Type: Resource Leak (Manual File Handling)
- Problem Location: `read_file` function: `f = open(filename, "r") ... f.close()`
- Detailed Explanation: If an exception occurs during `f.read()`, the `f.close()` line will never be executed, leaving the file handle open. While Python's garbage collector eventually handles this, it is a bad practice that can lead to "too many open files" errors in larger systems.
- Improvement Suggestions: Use the `with open(filename, "r") as f:` context manager, which guarantees the file is closed regardless of whether an exception is raised.
- Priority Level: Medium

- Code Smell Type: Poor Error Propagation / Silent Failures
- Problem Location: `process_data` function
- Detailed Explanation: The function wraps almost every operation in a `try...except` block that returns `0`, `[]`, or `None`. This "swallows" errors, meaning the `main()` function will print a result (like `Results: 0`) even if the file was missing or the data was completely corrupted, providing no indication to the user that the process failed.
- Improvement Suggestions: Remove the internal `try...except` blocks within `process_data`. Allow exceptions to bubble up to the `main()` function or a dedicated error handler where they can be logged and reported properly.
- Priority Level: Medium