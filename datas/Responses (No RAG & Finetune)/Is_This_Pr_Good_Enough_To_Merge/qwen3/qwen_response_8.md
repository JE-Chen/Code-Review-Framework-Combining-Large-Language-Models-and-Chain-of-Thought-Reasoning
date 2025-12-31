[Review Report]
1. Correctness: The code correctly addresses the issues of unpropagated exceptions, incorrect exception type, and missed file modification detection. Validation logic is now correctly placed before signaling the last bytes to the subscriber, and the exception type is now `SdkClientException` (non-retryable). Tests cover all failure scenarios thoroughly.

2. Readability & Maintainability: The code introduces a method with excessive cognitive complexity (21 vs. allowed 15). The `validateFileUnchangedAndSignalErrors` method is difficult to read due to nested conditionals and multiple error handling paths. The test class has unnecessary public visibility, and tests use `Thread.sleep()` which is not recommended for test stability.

3. Consistency: The code follows the project's coding standards and architectural patterns. The builder pattern is implemented consistently, and the new `modifiedTimeAtStart` and `sizeAtStart` fields are properly integrated. The exception type change aligns with the SDK's error handling conventions.

4. Performance & Resource Usage: The changes are performance-neutral. File metadata is now captured once at request start (not per chunk), and validation happens only once at the end of the read. There are no unnecessary I/O operations or resource leaks.

5. Security: No security vulnerabilities are introduced. The exception messages don't leak sensitive information. File metadata checks use standard Java NIO APIs without security risks.

6. Impact Scope: The changes are limited to `FileAsyncRequestBody` and its tests. The API is extended with optional builder methods (backward compatible). The behavior of existing code remains unchanged. Rollback is straightforward by reverting the changes.

7. Testing: Tests are comprehensive and cover all failure scenarios described in the PR. The new tests verify exception types and messages correctly. Test coverage (81.58%) meets the required threshold (≥80.0%).

[Conclusion]
Do Not Merge

[Improvement Suggestions]
- Reduce the cognitive complexity of `validateFileUnchangedAndSignalErrors` from 21 to ≤15 by extracting validation logic into separate methods (e.g., `validateFileSize`, `validateModifiedTime`).
- Change the test class visibility from `public` to default (package-private) to follow JUnit 5 best practices.
- Replace `Thread.sleep()` in tests with more reliable time-based validation (e.g., using `Instant` comparisons or mocking file modification times).
- Add a comment explaining why the file metadata validation must happen before signaling the last bytes to the subscriber.