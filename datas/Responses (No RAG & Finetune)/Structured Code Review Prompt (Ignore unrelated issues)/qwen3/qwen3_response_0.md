[PR Summary]  
This PR addresses issues with file modification detection in FileAsyncRequestBody by ensuring exceptions are properly propagated, changing exception type to non-retryable SdkClientException, and capturing file metadata consistently for retries/splits.

[Key Improvements]  
- File modification validation now occurs before signaling last bytes to subscriber, ensuring errors are propagated before Netty cancels subscription.  
- Exceptions are now SdkClientException (non-retryable) instead of IOException.  
- File metadata (modifiedTimeAtStart and sizeAtStart) is captured consistently during FileAsyncRequestBody construction.  

[Improvement Suggestions]  
No improvements needed.

[Meets Requirements]  
Yes

[Summary: Merge Decision]  
Merge

[Reason]  
The code changes correctly address all three issues described in the PR. The validation logic is moved to the correct location to ensure errors are propagated before cancellation, the exception type is changed to non-retryable SdkClientException, and file metadata is captured consistently. The test code has been updated to verify the new behavior, and all test cases now check for the correct exception type.

[Additional Notes]  
None.