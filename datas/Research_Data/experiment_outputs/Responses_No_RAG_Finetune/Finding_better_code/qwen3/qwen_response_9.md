# Code Review: FileAsyncRequestBody Enhancement

## Analysis Summary

The PR correctly addresses three critical issues with file modification detection in `FileAsyncRequestBody`. The implementation is well-reasoned, with clear justification for each change. The core problem was that file modification checks were happening too late (after Netty had already canceled the subscription), and the exceptions were incorrectly classified as retryable. The solution moves validation to the final read operation, uses the correct exception type, and ensures consistent file state tracking across retries/splits.

## Key Improvements

1. **Error Propagation Timing**  
   The validation now occurs *before* the final `onNext` call (when `remainingBytes == 0`), ensuring the error is signaled before Netty cancels the subscription. This is the critical fix for the first issue.

2. **Non-Retryable Exception Type**  
   Switching from `IOException` to `SdkClientException` correctly marks this as a terminal error. This aligns with AWS SDK design principles where client-side errors (like file modification) shouldn't be retried.

3. **Consistent File State Tracking**  
   Capturing `modifiedTimeAtStart` and `sizeAtStart` at construction time (not per-read) ensures consistent validation across retries and split parts. This resolves the third issue.

## Code Review

### Strengths
- **Clear Intent**: The changes directly address each issue with minimal code changes
- **Error Messages**: Improved messages provide actionable information (e.g., "File last-modified time changed...")
- **Test Coverage**: Added comprehensive tests for all scenarios
- **Builder Pattern**: Properly extended the builder with optional parameters
- **Null Safety**: Handles `IOException` during file state capture gracefully

### Minor Improvements

1. **Error Message Consistency**  
   The error messages are good but could be more consistent in formatting. Consider using a single message template with parameters rather than concatenating strings.

2. **File State Capture**  
   The current approach of capturing state in the builder is correct, but the `sizeAtStart` field could be more explicitly typed. Since `Files.size()` returns `long`, `sizeAtStart` should be `Long` (which it is) to distinguish from `null` vs. `0`.

3. **Validation Order**  
   The validation order is correct (size check first, then modification time), but could be slightly optimized by checking `sizeAtStart == null` first to avoid unnecessary `Files.size()` calls.

## Revised Code (Minor Improvements)

```java
// In FileAsyncRequestBody.java (constructor)
if (builder.sizeAtStart != null) {
    this.sizeAtStart = builder.sizeAtStart;
} else {
    try {
        this.sizeAtStart = Files.size(path);
    } catch (IOException e) {
        log.debug(() -> "Failed to get file size for path " + path, e);
        this.sizeAtStart = null;
    }
}

// In validateFileUnchangedAndSignalErrors()
if (sizeAtStart == null) {
    signalOnError(SdkClientException.create("File size could not be determined at start"));
    return false;
}

if (sizeAtStart != sizeAtEnd) {
    signalOnError(SdkClientException.create("File size changed after reading started. Initial: %d, Current: %d", 
                                          sizeAtStart, sizeAtEnd));
    return false;
}
// ... rest of validation
```

## Why This Is Better

1. **More Defensive Validation**  
   Checking `sizeAtStart == null` before comparing sizes avoids `NullPointerException` when file size couldn't be determined at start (though the current code would throw NPE in `Files.size(path)` if `sizeAtStart` was null - this is already handled by the `sizeAtStart != null` check).

2. **Better Error Messages**  
   Using parameterized strings (like `String.format`) makes the messages more maintainable and avoids string concatenation issues.

3. **Clearer Intent**  
   The explicit `sizeAtStart == null` check makes the validation logic more readable to maintainers.

## Final Assessment

The PR is well-executed with minimal risk. The changes are:
- **Correct**: Fixes all three issues
- **Minimal**: Only modifies the necessary parts
- **Safe**: Handles edge cases with proper error logging
- **Maintainable**: Clear separation of concerns

The only minor improvement would be in the error message formatting, but this is purely stylistic. The current implementation is production-ready and aligns with AWS SDK's error handling patterns. The tests added are sufficient to verify the behavior.

**Recommendation: Approve as-is with minor note about error message formatting (optional)**. The implementation is already excellent and meets all requirements. The suggested improvement to parameterized messages would be a nice-to-have but not required for this PR.