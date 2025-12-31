# PR Review: Surface errors from FileAsyncRequestBody when files are modified during request

## Conclusion
**Do Not Merge**

## Analysis

The PR addresses critical issues related to file modification detection in `FileAsyncRequestBody`, which is important for ensuring data integrity during uploads. The changes are well-motivated and address all three stated issues:

1. **Propagating errors correctly** - Moving validation before `signalOnNext` ensures errors are signaled before Netty cancels the subscription.
2. **Non-retryable exceptions** - Changing from `IOException` to `SdkClientException` properly indicates this is a terminal error.
3. **Consistent metadata across splits** - Capturing `modifiedTimeAtStart` and `sizeAtStart` during construction ensures consistent values across retries/splits.

The code changes are logical, well-documented, and the new tests comprehensively verify the behavior. The exception messages are clear and include helpful diagnostic information.

## Critical Quality Issues

Despite the important fixes, the PR contains critical quality issues that must be addressed before merging:

1. **High Cognitive Complexity** (Java rule `java:S3776`):
   - The `validateFileUnchangedAndSignalErrors()` method has a cognitive complexity of 21, which exceeds the 15 allowed threshold.
   - High cognitive complexity makes code harder to understand, maintain, and debug.

2. **JUnit5 Test Visibility** (Java rule `java:S5786`):
   - JUnit 5 test classes and methods should have default package visibility (not `public`).
   - This is a minor but important convention for test code.

3. **Thread.sleep() in Tests** (Java rule `java:S2925`):
   - Using `Thread.sleep()` in tests is discouraged as it makes tests flaky and slow.
   - Tests should use more robust synchronization mechanisms.

## Improvement Suggestions

1. **Refactor `validateFileUnchangedAndSignalErrors()` to reduce cognitive complexity**:
   ```java
   private boolean validateFileUnchangedAndSignalErrors() {
       return validateFileSize() && validateModificationTime();
   }
   
   private boolean validateFileSize() {
       try {
           long sizeAtEnd = Files.size(path);
           if (sizeAtStart != sizeAtEnd) {
               signalOnError(SdkClientException.create("File size changed after reading started. Initial size: " + sizeAtStart + ". Current size: " + sizeAtEnd));
               return false;
           }
           if (remainingBytes.get() > 0) {
               signalOnError(SdkClientException.create("Fewer bytes were read than were expected, was the file modified after reading started?"));
               return false;
           }
           return true;
       } catch (NoSuchFileException e) {
           signalOnError(SdkClientException.create("Unable to check file status after read. Was the file deleted or were its permissions changed?", e));
           return false;
       } catch (IOException e) {
           signalOnError(SdkClientException.create("Unable to check file status after read.", e));
           return false;
       }
   }
   
   private boolean validateModificationTime() {
       try {
           FileTime modifiedTimeAtEnd = Files.getLastModifiedTime(path);
           if (modifiedTimeAtStart.compareTo(modifiedTimeAtEnd) != 0) {
               signalOnError(SdkClientException.create("File last-modified time changed after reading started. Initial modification time: " + modifiedTimeAtStart + ". Current modification time: " + modifiedTimeAtEnd));
               return false;
           }
           return true;
       } catch (IOException e) {
           signalOnError(SdkClientException.create("Unable to check file status after read.", e));
           return false;
       }
   }
   ```

2. **Change test visibility to default package-private**:
   - Remove the `public` modifier from all test classes and methods
   - Example: Change `public class FileAsyncRequestBodyTest {` to `class FileAsyncRequestBodyTest {`

3. **Replace `Thread.sleep()` with a timeout loop**:
   ```java
   // Replace:
   Thread.sleep(1_000);
   
   // With:
   long startTime = System.currentTimeMillis();
   while (System.currentTimeMillis() - startTime < 1000) {
       Thread.sleep(10);
   }
   ```

4. **Consolidate changelog entries**:
   - The PR adds two separate changelog entries for the same fix. Consolidate into a single entry.

## Additional Notes

The PR description is well-written and provides clear motivation for the changes. The test coverage is good, and the new test cases thoroughly verify the expected behavior.

The exception message format is excellent and includes all necessary diagnostic information for users to understand what happened.

## Final Recommendation

The PR contains important fixes that should be merged, but **it must be updated to address the quality issues** (especially the cognitive complexity) before merging. Once these issues are resolved, the PR should be re-reviewed and approved.

**Do Not Merge** - Requires fixes to quality issues before consideration.