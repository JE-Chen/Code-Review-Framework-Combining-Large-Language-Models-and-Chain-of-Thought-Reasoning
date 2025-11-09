# Code Review: PR for File Modification Detection in FileAsyncRequestBody

## Conclusion
**Do Not Merge**

The PR addresses a critical bug with a well-motivated solution, but it contains quality issues that must be fixed before merging. The cognitive complexity issue is particularly concerning as it impacts maintainability and code quality standards.

## Improvement Suggestions

1. **Reduce Cognitive Complexity** (Critical Fix Required)
   - The method `validateFileUnchangedAndSignalErrors()` has a cognitive complexity of 21, exceeding the allowed 15.
   - **Fix**: Break the method into smaller, focused methods as shown in the refactoring example below:
     ```java
     private boolean validateFileUnchangedAndSignalErrors() {
         if (!validateFileSize()) {
             return false;
         }
         if (!validateModificationTime()) {
             return false;
         }
         return true;
     }
     
     private boolean validateFileSize() {
         // Existing file size validation logic
     }
     
     private boolean validateModificationTime() {
         // Existing modification time validation logic
     }
     ```
   - This reduces the cognitive complexity of the main method to 3 (just the two method calls) while distributing the complexity across smaller, focused methods.

2. **Fix Test Visibility** (Minor)
   - The test class and methods have `public` visibility, which is not recommended for JUnit 5 tests.
   - **Fix**: Change the visibility to package-private (remove `public` modifier) for the test class and methods.

3. **Replace Thread.sleep() in Tests** (Minor)
   - The PR uses `Thread.sleep()` in tests, which is discouraged as it makes tests slow and flaky.
   - **Fix**: Use a loop with a short sleep and check instead of a fixed sleep time:
     ```java
     // Before
     Thread.sleep(1_000);
     Files.setLastModifiedTime(testFile, FileTime.from(Instant.now()));
     
     // After
     FileTime initialModifiedTime = Files.getLastModifiedTime(testFile);
     Files.setLastModifiedTime(testFile, FileTime.from(Instant.now().plusMillis(100)));
     int attempts = 0;
     FileTime newModifiedTime = Files.getLastModifiedTime(testFile);
     while (newModifiedTime.equals(initialModifiedTime) && attempts < 10) {
         Thread.sleep(100);
         newModifiedTime = Files.getLastModifiedTime(testFile);
         attempts++;
     }
     ```

4. **Clarify Documentation** (Minor)
   - The Javadoc for `modifiedTimeAtStart` and `sizeAtStart` could be more specific about when these values are used and why they're needed.
   - **Suggestion**: Add a note that these values are used to detect file modifications during the request.

5. **Consider Additional Validation** (Optional)
   - The PR ensures that file modifications are detected, but it might be helpful to add a test that verifies the behavior when the file is modified *before* the request starts (though the current tests cover the main use case).

## Why This PR Should Not Be Merged

The cognitive complexity issue is significant because it:
- Makes the code harder to understand and maintain
- Increases the risk of future bugs
- Violates the SDK's quality standards

The other two issues (test visibility and Thread.sleep()) are minor but still need to be fixed as they represent poor testing practices and violate quality standards.

## Additional Notes

The solution itself is well-designed and addresses the core problem correctly:
- Moving the validation to before sending the last bytes ensures errors are propagated
- Changing to `SdkClientException` is correct (non-retryable)
- Capturing file metadata at construction time ensures consistency across retries/splits

The PR has excellent documentation, tests, and a clear explanation of the problem. The only issues are the quality problems that need to be fixed before merging.

## Final Recommendation

Fix the cognitive complexity issue, test visibility issue, and replace the Thread.sleep() in tests. After these fixes are made, the PR will be of sufficient quality to be merged.