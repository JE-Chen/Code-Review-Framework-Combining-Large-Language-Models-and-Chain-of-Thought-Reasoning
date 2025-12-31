# PR Review: FileAsyncRequestBody Modification Detection

## Conclusion
**Do Not Merge**

The PR addresses a legitimate issue with file modification detection in `FileAsyncRequestBody`, but contains several code quality issues that must be resolved before merging. The changes are important and well-motivated, but the code quality issues are significant enough to block the merge.

## Improvement Suggestions

1. **Reduce Cognitive Complexity** (Critical Issue)
   - The `validateFileUnchangedAndSignalErrors` method has a cognitive complexity of 21, exceeding the allowed 15.
   - **Fix**: Refactor the method to reduce complexity by extracting smaller, focused methods for each validation check:
     ```java
     private boolean validateFileUnchangedAndSignalErrors() {
         if (!validateFileSize()) return false;
         if (!validateFileModifiedTime()) return false;
         return true;
     }
     
     private boolean validateFileSize() {
         // File size validation logic
     }
     
     private boolean validateFileModifiedTime() {
         // File modification time validation logic
     }
     ```

2. **Remove Thread.sleep() from Tests** (Critical Issue)
   - The test `preset_modifiedTime_failsBecauseUpdatedModificationTime` uses `Thread.sleep()` which is not recommended in tests.
   - **Fix**: Replace with a more reliable test approach that doesn't depend on timing:
     ```java
     // Instead of:
     Thread.sleep(1_000);
     
     // Consider using a test utility to wait for the file to be modified
     // or use a different test strategy that doesn't require waiting
     ```

3. **Fix Test Visibility** (Minor Issue)
   - JUnit 5 tests should not have `public` visibility for classes and methods.
   - **Fix**: Remove `public` modifier from test class and methods:
     ```java
     // Change from:
     public class FileAsyncRequestBodyTest {
     
     // To:
     class FileAsyncRequestBodyTest {
     ```

4. **Add Test for null modifiedTimeAtStart** (Recommended)
   - While the constructor handles null values, it would be good to add a specific test for this scenario to ensure it's properly handled.

5. **Consider Adding File Metadata Validation in Builder** (Recommended)
   - Add validation in the builder to ensure that `modifiedTimeAtStart` and `sizeAtStart` are provided consistently if they're used.

## Why This Matters

The cognitive complexity issue is the most critical as it affects maintainability and readability of a method that's crucial for error handling. The `Thread.sleep()` in tests is a common anti-pattern that can cause flaky tests and should be avoided. The visibility issue is a minor but important coding standard that should be followed.

The change itself is well-justified and necessary - the previous behavior would silently fail if a file was modified during upload, which is a serious issue for users. The fix to change from `IOException` to `SdkClientException` is particularly important as it correctly marks this as a terminal error rather than a retryable one.

## Additional Notes

The documentation and test coverage are good, and the new exception message is descriptive and helpful for users. The change to capture the file metadata at construction time (rather than per-part) is the right approach for consistency across retries and splits.

The PR is otherwise well-structured and addresses the issues correctly. The suggested fixes are relatively minor and would significantly improve the quality of the code.

**Action Required**: Fix the three issues listed above before merging. The PR is otherwise excellent and addresses a critical issue with the SDK.