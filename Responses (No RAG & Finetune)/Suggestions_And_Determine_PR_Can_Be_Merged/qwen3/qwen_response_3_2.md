# PR Review: File Modification Error Propagation

## Verdict: Do Not Merge

## Reasoning

### Correctness & Contract Compliance
- ✅ The core fix correctly handles file modification validation at the right timing (before signaling `onNext`).
- ✅ Uses `SdkClientException` appropriately instead of raw `IOException` for SDK-level errors.
- ✅ Validation logic properly checks size, modification time, and byte count.
- ⚠️ The validation logic in `validateFileUnchangedAndSignalErrors` is placed at the right point but is overly complex, increasing the risk of correctness issues.

### Impact Analysis
- ✅ Minimal API changes (two new optional builder methods).
- ✅ No breaking changes to existing functionality.
- ⚠️ The high cognitive complexity increases the risk of subtle bugs in the validation logic.
- ⚠️ The `Thread.sleep()` in tests introduces flakiness and slow test execution.

### Code Quality & Maintainability
- ⚠️ **Cognitive Complexity**: `validateFileUnchangedAndSignalErrors` has a complexity of 21 (exceeding the recommended max of 15). This violates the project's quality standards and makes the code harder to maintain.
- ⚠️ **Unnecessary Public Test Modifiers**: Test class and methods are marked `public` when they should be package-private (per JUnit 5 best practices).
- ✅ Good naming and documentation for new API elements.
- ⚠️ The validation logic is not modularized, making it harder to understand and maintain.

### Testing & Verification
- ✅ Comprehensive test coverage for all validation scenarios (size change, modification time change, file deletion).
- ⚠️ **Flaky Tests**: The use of `Thread.sleep()` in tests makes them:
  1. Non-deterministic (tests may fail on slow systems)
  2. Slower than necessary (adding unnecessary execution time)
  3. Unreliable (if sleep time is insufficient, tests may fail)
- ✅ Error messages and exception types are correctly verified.

### Merge Readiness Summary
**Strengths**: The core fix is correct and well-justified. The test coverage is comprehensive for the new behavior.

**Weaknesses**: The code quality issues (especially cognitive complexity) and test quality issues (use of `Thread.sleep()`) are significant enough to prevent merging. These issues violate the project's quality standards and could lead to maintenance problems.

## Action Items (Prioritized)

1. **Refactor `validateFileUnchangedAndSignalErrors`** to reduce cognitive complexity to ≤15 by breaking it into smaller, focused methods:
   ```java
   private boolean validateFileSize() {
       // Check file size
   }
   
   private boolean validateModificationTime() {
       // Check modification time
   }
   
   private boolean validateFileUnchangedAndSignalErrors() {
       if (!validateFileSize()) return false;
       if (!validateModificationTime()) return false;
       return true;
   }
   ```

2. **Replace `Thread.sleep()` in tests** with a deterministic time-based check:
   ```java
   // Instead of Thread.sleep(1000)
   FileTime initialModifiedTime = Files.getLastModifiedTime(testFile);
   Instant targetTime = Instant.now().plusSeconds(1);
   while (Instant.now().isBefore(targetTime)) {
       // Wait for time to advance
   }
   Files.setLastModifiedTime(testFile, FileTime.from(Instant.now()));
   ```

3. **Make test class/methods package-private** (remove `public` modifiers):
   - Change `public class FileAsyncRequestBodyTest` to `class FileAsyncRequestBodyTest`
   - Change `public void preset_modifiedTime_failsBecauseUpdatedModificationTime()` to `void preset_modifiedTime_failsBecauseUpdatedModificationTime()`

4. **Add edge case test for time resolution** (optional but recommended):
   - Test behavior when file modification time changes by less than the resolution of `Files.getLastModifiedTime()` (though this is less likely to be an issue in practice).

## Why This Matters
The cognitive complexity issue is particularly concerning for a core SDK component that handles file I/O. The current implementation is difficult to verify for correctness and could lead to subtle bugs. The test quality issues make the test suite less reliable, which is unacceptable for a fundamental SDK component. Addressing these issues is critical before merging.