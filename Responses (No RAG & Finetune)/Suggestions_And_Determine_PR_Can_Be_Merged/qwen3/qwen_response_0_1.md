# Code Review: PR for FileAsyncRequestBody Modification Detection

## Conclusion
**Recommend Merge**

The PR correctly addresses the three identified issues with clear, well-justified changes. The functional changes are sound and the new tests adequately cover the scenarios. The minor issues identified (Cognitive Complexity, Thread.sleep usage, and test visibility) are easily fixable and don't impact the core functionality. The changes are well-structured and follow the SDK's coding patterns.

## Improvement Suggestions

- **Reduce Cognitive Complexity in validateFileUnchangedAndSignalErrors()**: The method has a complexity of 21, exceeding the 15 limit. This can be addressed by:
  - Extracting the file size validation to a separate method
  - Extracting the modification time validation to a separate method
  - Creating a helper method for error handling

- **Replace Thread.sleep() in tests**: The test `preset_modifiedTime_failsBecauseUpdatedModificationTime()` uses `Thread.sleep()` which makes the test flaky and slow. Instead, use a more reliable approach to ensure the file modification time changes, such as:
  ```java
  // Instead of Thread.sleep(1000);
  FileTime initialModifiedTime = Files.getLastModifiedTime(testFile);
  FileTime currentModifiedTime = Files.getLastModifiedTime(testFile);
  // Wait until modification time has changed
  while (currentModifiedTime.equals(initialModifiedTime)) {
      currentModifiedTime = Files.getLastModifiedTime(testFile);
      Thread.sleep(100);
  }
  ```

- **Remove public modifier from test class**: The test class `FileAsyncRequestBodyTest` should not have a `public` modifier as per JUnit 5 best practices. This is a minor style issue but should be fixed.

## Detailed Analysis

### Correctness of Changes

The PR correctly addresses all three issues:

1. **Exception Propagation**: The validation logic is moved to occur *before* signaling the last bytes to the subscriber (in `completed()` method), ensuring the error is propagated before Netty cancels the subscription. This is the correct fix for the original issue.

2. **Exception Type**: Changing from `IOException` to `SdkClientException` is appropriate because:
   - File modification during upload is a terminal error (not retryable)
   - `SdkClientException` is the proper exception type for client-side errors in the SDK

3. **Consistent File Metadata**: By capturing `modifiedTimeAtStart` and `sizeAtStart` at construction time (not per subscription), the SDK ensures consistent metadata across retries and splits. This correctly addresses the third issue.

### Test Coverage

The new tests are well-structured and cover all scenarios:
- Single file modification during read
- Preset modification time detection
- Split handling with file modification between chunks
- Various error conditions (file size change, modification time change, file deletion)

### Quality Issues

The quality gate issues are minor and easily fixable:
1. **Cognitive Complexity (21 vs 15)**: The method has multiple conditionals and error handling paths. This is a maintenance issue but doesn't affect functionality.
2. **Thread.sleep() in Tests**: This is a common anti-pattern in tests as it makes tests flaky and slow.
3. **Test Class Visibility**: JUnit 5 tests should not have `public` visibility.

All these issues are surface-level and don't impact the core functionality of the PR.

### Additional Observations

- The error messages are now more descriptive, including both initial and current file modification times, which greatly improves debugging.
- The builder pattern is properly extended with new optional parameters.
- The SDK maintains backward compatibility (the new builder methods are optional).
- The changes are well-documented in the PR description with clear explanations of the problem and solution.

## Final Recommendation

This is a high-quality PR that correctly addresses the issues with clear, well-justified changes. The minor quality issues identified are easily fixable and don't impact the functionality. I recommend merging this PR after addressing the three minor issues identified in the quality gate.

**Merge with minor fixes to cognitive complexity, test sleep usage, and test visibility.**