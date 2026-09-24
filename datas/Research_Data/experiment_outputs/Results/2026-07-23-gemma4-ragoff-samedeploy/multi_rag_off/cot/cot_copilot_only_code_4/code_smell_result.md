- Code Smell Type: Magic Numbers (Sentinel Values)
- Problem Location: `risky_division` (returns `9999`, `-1`), `convert_to_int` (returns `0`, `-999`), `read_file` (returns `"FILE_NOT_FOUND"`)
- Detailed Explanation: The functions use arbitrary numbers or strings to signal errors instead of raising exceptions or returning a structured result (like `None` or a Result object). This forces the caller to know these specific "magic" values to handle errors, which is error-prone and makes it impossible to distinguish between a legitimate result (e.g., a division that actually equals 9999) and an error.
- Improvement Suggestions: Raise custom exceptions or return `None` if the value is missing. Let the calling function decide how to handle the failure.
- Priority Level: High

- Code Smell Type: Over-generalized Exception Handling (Pokemon Exception Handling)
- Problem Location: `except Exception as e:` and `except Exception:` blocks in every function.
- Detailed Explanation: Catching the base `Exception` class hides bugs and makes debugging extremely difficult. For example, in `process_data`, a `TypeError` or `KeyboardInterrupt` would be silently swallowed and converted to `None` or `0`, masking the root cause of the failure.
- Improvement Suggestions: Catch only the specific exceptions expected (e.g., `ValueError`, `IOError`). Remove the generic `except Exception` blocks unless they are at the very top level of the application for logging purposes.
- Priority Level: High

- Code Smell Type: Resource Leak (Manual File Handling)
- Problem Location: `read_file` function (`f = open(filename, "r") ... f.close()`)
- Detailed Explanation: If an exception occurs during `f.read()`, the `f.close()` line will never be executed, leaving the file handle open. This can lead to resource exhaustion in larger applications.
- Improvement Suggestions: Use a `with` statement (context manager) to ensure the file is closed automatically regardless of whether an exception is raised.
- Priority Level: Medium

- Code Smell Type: Deeply Nested Try-Except Blocks
- Problem Location: `process_data` function.
- Detailed Explanation: The function contains three levels of nested `try-except` blocks. This "pyramid of doom" significantly reduces readability and makes the control flow difficult to follow.
- Improvement Suggestions: Flatten the logic. Since `convert_to_int` and `risky_division` already handle their own exceptions, the outer `try-except` blocks in `process_data` are largely redundant.
- Priority Level: Medium