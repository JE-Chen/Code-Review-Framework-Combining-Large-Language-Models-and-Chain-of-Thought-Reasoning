# PR Review: Surface errors from FileAsyncRequestBody when files are modified during request

## Conclusion
**Recommend Merge**

## Analysis

This PR addresses critical issues related to file modification detection in the AWS SDK for Java v2's `FileAsyncRequestBody` implementation. The changes are well-structured, thoroughly tested, and address all the problems outlined in the PR description.

### Key Strengths

1. **Corrected error propagation timing**:
   - The PR moves the file validation check to occur *before* `signalOnNext` (which would trigger Netty to call `cancel`), ensuring errors are properly signaled before subscription cancellation. This directly resolves the core issue described in the motivation.

2. **Appropriate exception type change**:
   - The PR correctly changes from `IOException` to `SdkClientException`, making these errors non-retryable as they should be. This is a crucial improvement for user experience and correctness.

3. **Consistent metadata capture**:
   - The PR ensures `modifiedTimeAtStart` and `sizeAtStart` are captured at construction time, not during subscription. This is critical for handling split requests and retries correctly, which was a major flaw in the original implementation.

4. **Comprehensive test coverage**:
   - The PR adds new tests covering:
     - File size changes
     - File modification time changes
     - Split requests with modifications between parts
     - Preset `modifiedTimeAtStart` values
   - Tests are well-written and verify the expected behavior.

5. **Robust error handling**:
   - The new `validateFileUnchangedAndSignalErrors` method handles all edge cases (file deletion, size changes, modification time changes) and properly converts exceptions to `SdkClientException`.

6. **Backward compatibility**:
   - The changes add optional builder methods (`modifiedTimeAtStart`, `sizeAtStart`) that don't break existing usage patterns.

## Improvement Suggestions

- **Add a comment explaining the critical timing change** in `FileAsyncRequestBody.java`:
  ```java
  // Validation must happen BEFORE signalOnNext to ensure errors are propagated
  // before Netty calls cancel() (which happens after onNext is called)
  if (remaining == 0) {
      closeFile();
      if (!validateFileUnchangedAndSignalErrors()) {
          return;
      }
  }
  ```
  This would make the critical implementation decision immediately clear to future maintainers.

- **Add a test for `sizeAtStart` provided with file size change**:
  While the PR covers the `modifiedTimeAtStart` scenario with preset values, adding a test case where `sizeAtStart` is provided and the file size changes would provide even more confidence in the implementation.

- **Add a test for `modifiedTimeAtStart` provided with no file modification**:
  A positive test case verifying that the error is *not* thrown when the file isn't modified after the initial snapshot would complement the existing negative test cases.

- **Consider adding a test for file modification with exact timestamp**:
  The current test uses `Thread.sleep(1_000)` to ensure the modification time is different, but adding a test that explicitly sets the modification time to a value that's exactly one second different would be more precise.

- **Add a comment in the test for `preset_modifiedTime_failsBecauseUpdatedModificationTime`**:
  The test currently uses `Thread.sleep(1_000)` to ensure the modification time changes. A comment explaining *why* this sleep is necessary (to ensure the timestamp changes) would improve test readability.

## Final Assessment

This is a high-quality PR that fixes a significant bug with excellent test coverage. The changes are well-designed, follow the SDK's coding conventions, and address all the issues described in the motivation. The only minor improvements suggested above would make an already solid PR even better, but they are not critical for the merge.

**The PR is ready to be merged.**