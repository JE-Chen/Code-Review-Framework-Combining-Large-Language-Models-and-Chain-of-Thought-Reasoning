[PR Summary]  
This PR fixes three issues related to file modification detection in FileAsyncRequestBody. It ensures errors are propagated correctly, changes exception type to non-retryable, and properly detects file modifications between retries/splits.

[Key Improvements]  
- File modification errors are now signaled before Netty cancels the subscription, ensuring they're propagated correctly.  
- Exceptions are now SdkClientException (non-retryable) instead of IOException (retryable).  
- File modification time and size are captured at request build time, ensuring consistency across retries and splits.

[Improvement Suggestions]  
- Reduce cognitive complexity of `validateFileUnchangedAndSignalErrors()` method (currently 21, max allowed is 15).  
- Replace `Thread.sleep()` with a synchronization mechanism in tests (e.g., using `CountDownLatch`).

[Meets Requirements]  
Yes

[Summary: Merge Decision]  
Merge

[Reason]  
The code correctly addresses all three issues described in the PR. The error propagation logic is now correctly positioned before Netty cancels the subscription. The exception type change from IOException to SdkClientException is appropriate for terminal errors. The file modification time and size are properly captured at build time for consistency across retries/splits. The test coverage verifies the new behavior correctly.

[Additional Notes]  
- The cognitive complexity issue and `Thread.sleep()` usage in tests are code quality improvements but do not affect correctness. They can be addressed in a separate PR.