[Review Report]
1. **Correctness**: The PR correctly addresses the three issues described in the motivation. The validation logic is moved to the correct place before `signalOnNext`, ensuring errors are propagated before Netty cancels the subscription. The exception type is changed from `IOException` to `SdkClientException`, which is appropriate for a terminal error. The file metadata capture is done at construction time, ensuring consistency across retries/splits. The tests cover the described scenarios and the manual testing results align with the expected behavior.

2. **Readability & Maintainability**: The code changes are well-structured and follow the project's conventions. However, the method `validateFileUnchangedAndSignalErrors` has a cognitive complexity of 21 (above the allowed 15), making it harder to understand and maintain. This needs to be refactored. The test class has a public modifier that should be removed, which is a minor readability issue.

3. **Consistency**: The code follows the project's coding standards and architectural patterns. The new builder methods (`modifiedTimeAtStart` and `sizeAtStart`) are consistent with other builder methods. The exception type change is consistent with the SDK's error handling practices.

4. **Performance & Resource Usage**: The changes introduce minimal performance overhead. The validation is done only once at the end of the read, and the file metadata is captured at construction time rather than repeatedly. The resource usage impact is negligible.

5. **Security**: No security issues are introduced. The exception message includes file metadata for debugging purposes, but this is not sensitive information. The code doesn't introduce any new security vulnerabilities.

6. **Impact Scope**: The changes are limited to the `FileAsyncRequestBody` class and its related tests. The behavior change is documented and tested. The change is non-breaking for existing users (the new behavior only affects file modification detection, which was previously broken).

7. **Testing**: The PR includes comprehensive new tests covering the scenarios described in the motivation. The tests use the correct assertions and match the expected behavior. The CI tests passed, and the coverage is above the required 80%.

[Conclusion]
Do Not Merge

[Improvement Suggestions]
- Refactor `validateFileUnchangedAndSignalErrors` to reduce cognitive complexity below 15 (e.g., by extracting sub-methods for file size check, file modification check, and exception handling).
- Remove the `public` modifier from the test class `FileAsyncRequestBodyTest` to follow JUnit 5 best practices.
- Replace `Thread.sleep(1_000)` in the test `preset_modifiedTime_failsBecauseUpdatedModificationTime` with a more reliable method to ensure the file modification time has changed (e.g., using `Instant.now().minusSeconds(2)` to set a known earlier time).
- Ensure the exception message is consistent with other SDK exception messages (e.g., "File last-modified time changed after reading started. Initial modification time: ...").
- Verify that the `modifiedTimeAtStart` and `sizeAtStart` are properly handled when they are `null` (e.g., when the file metadata cannot be retrieved).