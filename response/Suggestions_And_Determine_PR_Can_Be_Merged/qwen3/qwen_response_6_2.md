# PR Review: Surface errors from FileAsyncRequestBody when files are modified during request

## Verdict
Do Not Merge

## Reasoning

- **Correctness & Contract Compliance**
  - The bug fix is well-motivated and correctly addresses the issue of file modification errors not being propagated properly
  - The validation logic is now correctly placed to occur before the final bytes are sent to the subscriber
  - Error signaling has been properly changed from `IOException` to `SdkClientException` (appropriate for terminal errors)
  - The validation timing is correct for ensuring errors are signaled at the right moment

- **Impact Analysis**
  - No backward compatibility issues - the changes are strictly additive (new fields, new builder methods)
  - The validation logic is limited to the final bytes check, so performance impact is minimal
  - All edge cases (file size changes, modification time changes, file deletion) are now covered

- **Code Quality & Maintainability**
  - **Critical issue**: The `validateFileUnchangedAndSignalErrors()` method has a cognitive complexity of 21, exceeding the project's recommended threshold of 15
  - The method contains multiple nested conditionals and error handling paths that make it difficult to understand and maintain
  - The test class and methods have public visibility, which violates JUnit 5 best practices (should be package-private)
  - The test `preset_modifiedTime_failsBecauseUpdatedModificationTime()` uses `Thread.sleep(1_000)` which is unreliable for test determinism

- **Testing & Verification**
  - Tests have been updated to cover all the new error cases
  - Tests now correctly use `SdkClientException` instead of `IOException`
  - Test cases cover both success and failure paths
  - The test cases are generally well-written but have the reliability issue with `Thread.sleep`

- **Merge Readiness**
  - The core bug fix is correct and well-implemented
  - The cognitive complexity violation is a major quality issue that must be addressed
  - The test visibility and sleep usage issues are minor but should be fixed as part of quality improvements

## Action Items (in priority order)

1. **Refactor `validateFileUnchangedAndSignalErrors()` to reduce cognitive complexity**:
   - Extract each validation check (file size, remaining bytes, modification time) into separate methods
   - This will reduce the complexity from 21 to a manageable level (likely 5-7 per extracted method)
   - Example:
     ```java
     private boolean validateFileSize() {
         // Existing size validation logic
     }
     
     private boolean validateModificationTime() {
         // Existing modification time validation logic
     }
     ```

2. **Replace `Thread.sleep` with a more reliable file modification check**:
   - Instead of waiting for 1 second, directly set the file modification time after creating the test file
   - Example:
     ```java
     // Create test file
     Path testFile = RandomTempFile.createTempFile("test", ".txt");
     
     // Capture initial modification time
     FileTime initialModifiedTime = Files.getLastModifiedTime(testFile);
     
     // Directly set new modification time without waiting
     Files.setLastModifiedTime(testFile, FileTime.from(Instant.now().plusSeconds(1)));
     ```

3. **Change test visibility to package-private**:
   - Change `public` test class and methods to default visibility
   - This aligns with JUnit 5 best practices and improves encapsulation

4. **Add a comment explaining the validation timing**:
   - Add a comment in the `FileSubscription` class explaining why validation occurs before sending the final bytes to the subscriber

5. **Add a test to verify `modifiedTimeAtStart` and `sizeAtStart` capture**:
   - Create a test that verifies these values are correctly captured at the start of the request

The PR addresses a critical bug but fails to meet the project's quality standards due to the high cognitive complexity. The suggested refactoring would make the code more maintainable while preserving the functionality. The other issues are minor but should be fixed as part of the quality improvements.