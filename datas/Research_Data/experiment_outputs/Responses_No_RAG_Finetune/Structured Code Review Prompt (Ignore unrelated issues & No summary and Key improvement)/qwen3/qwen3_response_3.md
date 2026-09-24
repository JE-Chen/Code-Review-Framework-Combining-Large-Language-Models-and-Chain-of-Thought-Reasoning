[Improvement Suggestions]  
- The reported cognitive complexity of 21 for `validateFileUnchangedAndSignalErrors` appears to be incorrect based on the actual code structure. The method has a reasonable complexity for its purpose and the logic is clear. No changes are needed for this issue.

[Meets Requirements]  
- Yes

[Summary: Merge Decision]  
- Merge

[Reason]  
The code correctly addresses the three issues described in the PR:
1. File modification validation is now performed before signaling the last bytes to the subscriber (ensuring errors are propagated before Netty cancels the subscription)
2. Exceptions are now `SdkClientException` (non-retryable) instead of `IOException`
3. `modifiedTimeAtStart` and `sizeAtStart` are captured when the `FileAsyncRequestBody` is constructed, ensuring consistency between retries/splits

The test changes properly verify the new behavior, and the reported issues from the static analysis tool are either false positives (public test methods in JUnit 5 must be public) or necessary test patterns (Thread.sleep for file modification timing).

[Additional Notes]  
- The cognitive complexity issue is likely a false positive from the static analysis tool. The method complexity is reasonable for the critical error handling logic.
- The Thread.sleep usage in tests is appropriate to ensure file modification time changes occur as expected.
- No other issues were found that would prevent merging this change.