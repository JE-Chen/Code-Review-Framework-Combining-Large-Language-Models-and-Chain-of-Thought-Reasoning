# PR Review: Surface errors from FileAsyncRequestBody when files are modified during request

## Conclusion
**Recommend Merge**

## Analysis

This PR addresses critical issues in the file modification detection logic within `FileAsyncRequestBody`. The changes are well-structured, properly tested, and significantly improve the SDK's reliability when dealing with file modification scenarios.

## Key Strengths

1. **Clear Problem Statement**: The PR clearly articulates the three related issues:
   - Unpropagated exceptions
   - Retryable exceptions for terminal errors
   - Inconsistent file state tracking between retries/splits

2. **Corrected Error Propagation**: The most critical fix moves validation *before* `signalOnNext` (which triggers Netty to cancel the subscription), ensuring errors are properly propagated to the user.

3. **Appropriate Exception Type**: Changing from `IOException` to `SdkClientException` is exactly correct since file modification is terminal and not retryable.

4. **Comprehensive Testing**: The added tests cover all critical scenarios:
   - File size changes (shorter/longer)
   - Modification time changes
   - File deletion
   - Split behavior with file modification between chunks
   - Preset modified time with file modification

5. **Minimal Impact**: The changes are focused and don't introduce new complexity or break existing behavior.

6. **Consistent Implementation**: The new builder methods and fields follow the SDK's existing patterns.

7. **Quality Metrics**: The PR meets all quality requirements (81.58% coverage > 80% requirement).

## Improvement Suggestions

1. **Changelog Entry Deduplication**: The PR includes two identical changelog entries (`bugfix-AWSSDKforJavav2-4bab915.json`). These should be merged into a single entry to avoid confusion.

2. **Exception Message Formatting**: The exception messages could be slightly more consistent with other SDK exception messages. For example:
   ```diff
   - "File last-modified time changed after reading started. Initial modification time: 2025-09-05T19:20:46.540910708Z. Current modification time: 2025-09-05T19:20:47.981202736Z (SDK Attempt Count: 1)"
   + "File last-modified time changed after reading started. Initial modification time: 2025-09-05T19:20:46.540910708Z. Current modification time: 2025-09-05T19:20:47.981202736Z"
   ```
   The "(SDK Attempt Count: 1)" is redundant since the SDK already includes attempt counts in the exception message.

3. **Error Message Consistency**: The test for "file gets shorter than already read" uses a different exception message than the other tests:
   ```java
   // In test
   .hasMessageContaining("File size changed after reading started")
   
   // In exception message
   "File size changed after reading started. Initial size: ... Current size: ..."
   ```
   The test message should match the exception message exactly.

4. **Builder Validation**: Consider adding validation in the builder to ensure that `modifiedTimeAtStart` and `sizeAtStart` are only set if the file is accessible (though this is a minor point as the SDK already handles these gracefully).

## Final Assessment

This is a high-quality PR that addresses critical issues with a clean, well-tested solution. The changes are appropriately scoped, the error handling is now correct, and the test coverage is thorough. The minor suggestions above are not blockers for merging.

The PR will significantly improve the user experience by ensuring file modification errors are properly reported and not treated as retryable errors. This prevents users from wasting time trying to retry requests that will fail due to file changes.

**Merge Recommendation: Approved**