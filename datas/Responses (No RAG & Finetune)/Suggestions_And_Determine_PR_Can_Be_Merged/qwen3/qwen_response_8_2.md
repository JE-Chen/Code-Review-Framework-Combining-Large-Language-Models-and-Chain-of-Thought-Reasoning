# PR Review: File Modification Error Handling

## Verdict
**Do Not Merge**

## Reasoning

### Correctness & Contract Compliance
- The change correctly addresses the bug of file modification exceptions not being propagated properly
- The solution follows SDK patterns by using `SdkClientException` instead of raw `IOException`
- The timing of the validation (after reading completes) is correct and ensures errors are signaled at the right time
- The error messages are descriptive and consistent with SDK error patterns

### Impact Analysis
- The change is backward-compatible (new builder methods are optional)
- The solution handles all edge cases: file size changes, modification time changes, and file deletion
- Performance impact is minimal (only two file metadata checks, one at start and one at end)
- No race conditions identified in the provided code

### Code Quality & Maintainability
- **Critical Issue**: `validateFileUnchangedAndSignalErrors()` has a cognitive complexity of 21 (exceeding the typical 15 limit), making it difficult to maintain
- The method attempts to do multiple validation checks in a single function, violating the single responsibility principle
- The test code uses `Thread.sleep()` which is not ideal for tests (introduces flakiness and unnecessary waiting)
- Test classes/methods are declared as `public` instead of package-private (standard JUnit practice)
- The code is well-structured in other aspects (field naming, builder pattern, etc.)

### Testing & Verification
- Tests are comprehensive and cover all failure cases (file size changes, modification time changes, file deletion)
- Tests use the correct exception type (`SdkClientException`) and message format
- Test messages are descriptive and match the error messages
- **Issue**: Test uses `Thread.sleep()` instead of a proper wait loop, which could cause flakiness

### Additional Concerns
- The method `validateFileUnchangedAndSignalErrors()` should be broken into smaller, focused methods
- The test for preset modified time (`preset_modifiedTime_failsBecauseUpdatedModificationTime()`) is well-written but needs to be fixed to avoid `Thread.sleep()`
- The test visibility (`public` instead of package-private) is a minor but important style violation

## Action Items (prioritized)

1. **Fix cognitive complexity** in `validateFileUnchangedAndSignalErrors()` by breaking it into smaller methods:
   - Create separate methods for file size validation, modification time validation, and remaining bytes validation
   - This will reduce cognitive complexity to an acceptable level

2. **Replace `Thread.sleep()` with a proper wait loop** in all tests:
   - For example, replace:
     ```java
     Thread.sleep(1_000);
     ```
     With:
     ```java
     long startTime = System.currentTimeMillis();
     while (System.currentTimeMillis() - startTime < 2000) {
         if (Files.getLastModifiedTime(testFile).compareTo(initialModifiedTime) != 0) {
             break;
         }
         Thread.sleep(100);
     }
     ```

3. **Change all test classes and methods to package-private** (remove `public` modifier):
   - This is standard practice for JUnit tests and improves code clarity

4. **Verify exception message consistency** against other SDK exceptions (though the messages appear to be well-formatted)

## Summary

The PR is addressing a genuine bug with a well-structured solution, and the tests are comprehensive. However, the high cognitive complexity of the main validation method and the use of `Thread.sleep()` in tests are significant enough to prevent merging. These are all fixable issues that should be addressed in a follow-up commit before merging.

The change is technically sound and well-motivated, but the code quality issues need to be resolved before it can be considered ready for merge.