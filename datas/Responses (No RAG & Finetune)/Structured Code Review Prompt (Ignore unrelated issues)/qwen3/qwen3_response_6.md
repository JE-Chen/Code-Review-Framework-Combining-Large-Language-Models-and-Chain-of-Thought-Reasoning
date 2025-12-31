[PR Summary]  
This PR fixes a critical bug where file modification errors in AsyncRequestBody#fromFile were not being propagated to the caller. It ensures errors are signaled before Netty cancels the subscription, changes the exception type to be non-retryable, and captures file metadata consistently across retries/splits.

[Key Improvements]  
- Moved file validation to occur before signaling the last bytes to ensure errors are propagated before Netty cancels the subscription.  
- Changed exception type from IOException to SdkClientException to prevent retrying on file modification errors.  
- Added builder parameters to capture file metadata at request start, ensuring consistent behavior across retries/splits.

[Improvement Suggestions]  
No improvements needed.

[Meets Requirements]  
Yes

[Summary: Merge Decision]  
Merge

[Reason]  
The PR correctly addresses all described issues. The code changes ensure file modification errors are properly propagated, use the correct exception type, and capture file metadata consistently. The test code verifies the expected behavior, and the minor issues with Thread.sleep() in tests are not critical for correctness.

[Additional Notes]  
None.