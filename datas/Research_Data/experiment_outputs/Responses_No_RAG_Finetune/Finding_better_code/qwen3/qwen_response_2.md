# Code Review: FileAsyncRequestBody Enhancement

## Summary
The PR correctly addresses the core issues with file modification detection during async file uploads. The implementation moves validation to the correct point in the lifecycle (before `onNext` for the last chunk), changes the exception type to `SdkClientException`, and ensures consistent start state across retries/splits. The code is well-structured and follows SDK best practices.

## Key Improvements & Minor Recommendations

### ✅ What's Done Well
1. **Correct Lifecycle Handling**: Validation now occurs *before* signaling the last bytes, ensuring errors propagate before Netty calls `cancel`.
2. **Non-Retryable Exception**: Switching from `IOException` to `SdkClientException` is appropriate since file modification is terminal.
3. **Consistent Start State**: Capturing `modifiedTimeAtStart` and `sizeAtStart` at construction time (not subscription time) ensures detection across retries/splits.
4. **Comprehensive Testing**: Tests cover all edge cases (file size changes, modification time changes, file deletion).

### ⚠️ Minor Improvement Needed
The error message for "fewer bytes" is slightly misleading:
```java
// Current message
"Fewer bytes were read than were expected, was the file modified after reading started?"

// Recommendation
"Fewer bytes were read than expected. Was the file modified or truncated after reading started?"
```
**Why?** The original message implies modification is the *only* possible cause, but a file could be truncated (not modified) without being modified. The revised message is more precise and matches the pattern of other error messages.

### 🔍 Other Observations
1. **Error Message Consistency**: All other error messages follow a consistent pattern (e.g., "File [attribute] changed after reading started..."), which is excellent.
2. **Null Handling**: Safe handling of `null` values for `modifiedTimeAtStart`/`sizeAtStart` (via builder) is appropriate.
3. **Performance**: Validation only occurs on the last chunk, so no performance impact.

## Revised Code Snippet (Error Message Fix)

Here's the minimal fix needed for the error message:

```java
// In FileAsyncRequestBody.java, validateFileUnchangedAndSignalErrors()
if (remainingBytes.get() > 0) {
    signalOnError(SdkClientException.create(
        "Fewer bytes were read than expected. Was the file modified or truncated after reading started?"));
    return false;
}
```

## Why This Revision is Better

| Original Message | Revised Message | Reason |
|------------------|----------------|--------|
| "Fewer bytes were read than were expected, was the file modified after reading started?" | "Fewer bytes were read than expected. Was the file modified or truncated after reading started?" | More precise (truncation is a valid cause, not just modification) and consistent with other error messages. Adds period for grammatical correctness. |

## Final Assessment

The PR is **well-structured and addresses all issues**. The only necessary change is the error message precision for the "fewer bytes" case. This is a minor but important improvement for user experience and clarity.

**No other changes are needed.** The implementation is production-ready and follows all best practices. The error message fix is the only change required to make this implementation perfect.

## Revised Code (For Context)

```java
// core/sdk-core/src/main/java/software/amazon/awssdk/core/internal/async/FileAsyncRequestBody.java

// Inside validateFileUnchangedAndSignalErrors()
if (remainingBytes.get() > 0) {
    signalOnError(SdkClientException.create(
        "Fewer bytes were read than expected. Was the file modified or truncated after reading started?"));
    return false;
}
```

This single change ensures the error message is both technically accurate and user-friendly, while maintaining consistency with the rest of the SDK's error messaging pattern.