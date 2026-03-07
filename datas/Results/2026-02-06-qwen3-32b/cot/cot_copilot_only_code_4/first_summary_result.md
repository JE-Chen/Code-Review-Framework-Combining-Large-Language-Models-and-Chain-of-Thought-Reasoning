# Code Review Summary

## Key Issues Identified
- **Broad exception handling** (violates RAG rules and best practices)
- **Magic values** for error recovery (9999, -1, "FILE_NOT_FOUND")
- **Inconsistent error handling** across functions
- **Missing documentation** for critical behavior
- **Silent failure** in core processing logic

## Specific Recommendations

1. **Replace broad exception handlers** with specific exceptions:
   ```python
   # Before (problematic)
   except Exception as e:
       print("Unexpected error:", e)
       return -1

   # After (corrected)
   except ZeroDivisionError:
       return 9999
   ```

2. **Eliminate magic values**:
   - Use `None` or custom error types instead of `-1`/`9999`
   - Replace `"FILE_NOT_FOUND"` with explicit error objects

3. **Fix silent failure in `process_data`**:
   ```python
   # Before (silently discards entire list on any error)
   try:
       numbers = [convert_to_int(x) for x in data.split(",")]
   except Exception:
       numbers = []

   # After (handles only expected failures)
   if not isinstance(data, str):
       return 0
   numbers = [convert_to_int(x) for x in data.split(",")]
   ```

4. **Add documentation**:
   ```python
   def risky_division(a: int, b: int) -> float:
       """Safely divides a by b. Returns 9999 on ZeroDivisionError."""
       try:
           return a / b
       except ZeroDivisionError:
           return 9999
   ```

## Critical Violations
| Function                | Violation                          | Why It Matters                     |
|-------------------------|------------------------------------|------------------------------------|
| `risky_division`        | Catches `Exception`                | Masks real bugs, hides errors      |
| `convert_to_int`        | Catches `Exception`                | Returns -999 for unexpected errors |
| `read_file`             | Returns "" on all exceptions       | Hides disk errors                  |
| `process_data`          | Silently discards list on errors   | Causes silent data loss            |

## Impact Scope
- **All error-prone functions** affected (core business logic)
- **Critical risk**: Silent failures could corrupt data processing results
- **Test coverage**: None for error paths (requires unit tests)

## Why This Matters
The broad exceptions violate RAG rules and make debugging impossible. For example:
- A `TypeError` in `convert_to_int` would return `-999` instead of revealing invalid input
- `read_file` would return empty string for disk permission errors
- The entire `process_data` flow could fail silently without any trace

## Items to Confirm
1. Should `risky_division` return a fallback value or propagate errors?
2. Are magic values like `9999` truly acceptable in business context?
3. Do we need to add explicit error logging instead of `print`?
4. Will callers handle `None` returns from `process_data`?

> **Recommendation**: Prioritize removing all broad exceptions first. This is the highest-impact fix and aligns with RAG rules. The magic values can be addressed in follow-up.