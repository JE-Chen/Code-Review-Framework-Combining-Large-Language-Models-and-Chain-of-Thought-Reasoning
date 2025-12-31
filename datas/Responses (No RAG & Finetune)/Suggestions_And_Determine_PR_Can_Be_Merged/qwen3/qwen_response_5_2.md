# PR Review: Surface errors from FileAsyncRequestBody when files are modified during request

**Verdict:** Do Not Merge

**Reasoning:**

- **Correctness & Contract Compliance:**
  - ✅ The changes correctly address the core issue of propagating file modification errors before the subscription is canceled.
  - ✅ The exception type is properly changed from `IOException` to `SdkClientException` (indicating a terminal client-side error).
  - ✅ The validation logic is comprehensive, checking file size, remaining bytes, and last-modified time.
  - ✅ The validation is moved to happen *before* signaling completion, ensuring errors are properly signaled.

- **Impact Analysis:**
  - ✅ The changes are backward compatible (optional parameters).
  - ✅ No performance impact (validation is done once at the end of the request).
  - ✅ All edge cases are covered by the new tests (file size changes, modification time changes, file deletion).

- **Code Quality & Maintainability:**
  - ❌ **Critical cognitive complexity issue:** The `validateFileUnchangedAndSignalErrors()` method has a cognitive complexity of 21 (exceeding the 15 threshold), making it hard to understand and maintain.
  - ❌ **Test code quality issues:**
    - Tests are marked as `public` (should be package-private for test classes/methods).
    - `Thread.sleep(1_000)` is used in tests, making them flaky and slow.
  - ❌ **Duplicate changelog entries:** Two separate changelog entries for the same fix.
  - ✅ The exception messages are excellent and include all necessary diagnostic information.

- **Testing & Verification:**
  - ✅ Comprehensive test coverage for all failure scenarios.
  - ✅ Tests correctly verify the exception type and message.
  - ❌ Tests contain problematic `Thread.sleep()` calls that should be replaced with more robust synchronization.

- **Merge Readiness:**
  - The PR contains important fixes that should be merged, but it has critical quality issues that must be addressed first.
  - The cognitive complexity issue is particularly problematic for maintainability.

**Action Items (prioritized):**

1. **Refactor `validateFileUnchangedAndSignalErrors()`** to reduce cognitive complexity by breaking it into smaller, focused methods (validateFileSize, validateModificationTime, etc.).

2. **Replace all `Thread.sleep()` calls** in tests with a timeout loop pattern:
   ```java
   // Replace:
   Thread.sleep(1_000);
   
   // With:
   long startTime = System.currentTimeMillis();
   while (System.currentTimeMillis() - startTime < 1000) {
       Thread.sleep(10);
   }
   ```

3. **Change test classes/methods** from `public` to package-private (remove `public` modifier).

4. **Consolidate the two changelog entries** into a single, clear entry.

5. **Add a comment** explaining why the validation happens before signaling completion (to prevent Netty from canceling the subscription before the error is signaled).

**Final Recommendation:**
The PR addresses a critical issue with proper error handling, but the quality issues (especially the high cognitive complexity) make it difficult to maintain and verify. Once these quality issues are addressed, the PR will be ready for merge.