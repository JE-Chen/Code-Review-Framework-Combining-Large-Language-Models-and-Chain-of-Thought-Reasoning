[PR Summary]  
This PR fixes the issue where file modification errors were not being propagated correctly in the FileAsyncRequestBody. It ensures errors are signaled before the subscriber calls cancel, changes the exception type to SdkClientException, and captures file metadata at the start of the request for consistent validation across retries/splits.

[Key Improvements]  
- Validation logic moved to before signaling the last bytes to the subscriber, ensuring errors are propagated correctly.
- Changed exception type from IOException to SdkClientException, making it clear that file modification is a terminal error.
- Captured file modification time and size at the start of the request, ensuring consistency between retries/splits.

[Improvement Suggestions]  
No improvements needed.

[Meets Requirements]  
Yes

[Summary: Merge Decision]  
Merge

[Reason]  
The code correctly addresses the three issues identified in the PR description. The validation logic is properly moved to ensure errors are signaled before cancellation, the exception type is changed to SdkClientException as requested, and file metadata is captured at the start of the request. The test coverage is sufficient and the changes are well-justified.

[Additional Notes]  
None.