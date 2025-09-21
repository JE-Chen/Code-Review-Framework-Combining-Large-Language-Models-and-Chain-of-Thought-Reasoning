# PR Review: File Modification Error Handling

## Conclusion
**Recommend Merge**

## Detailed Analysis

### Problem Addressed
The PR correctly identifies and solves three critical issues:
1. File modification errors were not propagated (due to timing issue with Netty cancellation)
2. Errors were `IOException` (retryable by default) when they should be terminal
3. File modifications between retries/splits were not detected

### Code Quality Assessment

**Strengths:**
- The solution moves the validation logic to before `signalOnNext`, ensuring errors are properly propagated before Netty cancels the subscription
- Changed exception type from `IOException` to `SdkClientException` (non-retryable), which is the correct approach for terminal errors
- Added proper builder methods to capture file metadata at request start
- Comprehensive tests added for:
  * File modification during single request
  * File modification between split parts
  * File size changes
  * File deletion
  * Preset file metadata (via builder)

**Technical Soundness:**
- The timing of the validation check is now correct - validation happens *before* signaling the last bytes to the subscriber
- The solution maintains proper thread safety (the validation happens in the context of the subscription)
- Error messages now include meaningful details (initial vs current modification times and sizes)
- The change properly handles edge cases (file metadata read failures via `null` values)

**Testing:**
- Tests cover all scenarios described in the PR
- New tests verify the exception type is `SdkClientException` (not `IOException`)
- Tests include both single request and split request scenarios
- All tests pass in CI

**Documentation:**
- PR description is exceptionally clear and well-structured
- Javadoc added for new builder methods
- Error messages are descriptive and include necessary context

### Improvement Suggestions

1. **Error Message Formatting**  
   Consider using a standardized date format (like `DateTimeFormatter.ISO_INSTANT`) for the timestamp in error messages to match other SDK error messages. The current default `FileTime.toString()` may not be as readable as a standardized format.

2. **Builder Validation**  
   The builder currently allows `modifiedTimeAtStart` and `sizeAtStart` to be set to `null`. While the code handles `null` properly, it might be clearer to:
   - Require these values to be provided (or not) through a different API design
   - Add a validation in the builder to ensure consistency

3. **Edge Case for File Metadata Reads**  
   The code handles failures when reading file metadata (setting to `null` and logging debug), but it might be helpful to add a test case where these reads fail during request execution.

4. **Performance Note**  
   The initial file metadata reads (`Files.getLastModifiedTime` and `Files.size`) are now done once per request. While this is a good change from the previous implementation, it's worth noting this involves system calls that could be expensive in high-volume scenarios. However, this is a reasonable trade-off for correctness.

## Final Recommendation

The PR is of high quality and addresses a critical issue with proper engineering. The changes are focused, well-documented, and thoroughly tested. The change to use `SdkClientException` instead of `IOException` is particularly important for preventing accidental retries on terminal errors.

**The PR should be merged.** It's a significant improvement to the SDK's reliability and error handling for file uploads.