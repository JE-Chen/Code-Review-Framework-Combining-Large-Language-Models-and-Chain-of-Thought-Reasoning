[PR Summary]  
This PR addresses three related issues with file modification detection in FileAsyncRequestBody: ensuring errors are properly propagated, using the correct non-retryable exception type, and consistently capturing file metadata at request start.

[Key Improvements]  
- Validation logic for file modifications is now executed before signaling the last bytes to the subscriber, ensuring errors are propagated before Netty cancels the subscription.
- Changed exception type from IOException to SdkClientException, which is non-retryable and appropriate for this terminal error case.
- File metadata (modified time and size) is now captured consistently at request start, ensuring it's not reset for each retry or split part.

[Improvement Suggestions]  
No improvements needed.

[Meets Requirements]  
Yes

[Summary: Merge Decision]  
Merge

[Reason]  
The code correctly implements all the required changes: validation logic is placed before signaling the last bytes, exceptions are now SdkClientException (non-retryable), and file metadata is consistently captured at request start. The tests verify the expected behavior, and there are no correctness issues in the implementation code.

[Additional Notes]  
None.