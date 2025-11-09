[PR Summary]  
The PR fixes an issue where file modification exceptions in FileAsyncRequestBody were not being propagated correctly. It ensures exceptions are signaled before Netty cancels the subscription, changes the exception type to SdkClientException (non-retryable), and maintains consistent file metadata across retries/splits.

[Key Improvements]  
- Moved file validation logic to occur before sending the last bytes to the subscriber, ensuring errors are propagated correctly.
- Changed exception type from IOException to SdkClientException to indicate the error is terminal.
- Added modifiedTimeAtStart and sizeAtStart fields to ensure consistent file metadata across retries/splits.

[Improvement Suggestions]  
- The validateFileUnchangedAndSignalErrors method has high cognitive complexity (21 vs allowed 15). Consider refactoring to reduce complexity, though this is not a critical issue for this PR.

[Meets Requirements]  
Yes

[Summary: Merge Decision]  
Merge

[Reason]  
The PR correctly addresses all three issues described in the PR. The changes ensure file modification errors are propagated before Netty cancels the subscription, use the appropriate non-retryable exception type, and maintain consistent file metadata across retries/splits. The test coverage is sufficient to verify the behavior.

[Additional Notes]  
None.