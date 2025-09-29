[PR Summary]  
- This PR fixes an issue where file modification exceptions in AsyncRequestBody#fromFile were not being propagated. It moves the validation logic to happen before the call to signalOnNext, changes the exception type from IOException to SdkClientException, and ensures the file modification time and size are captured consistently between retries/splits.

[Key Improvements]  
- Fixed propagation of file modification exceptions by moving validation before signalOnNext  
- Changed exception type from IOException to SdkClientException to prevent retrying on file modifications  
- Added consistent capture of file modification time and size at start of request  

[Improvement Suggestions]  
- No improvements needed.  

[Meets Requirements]  
- Yes  

[Summary: Merge Decision]  
- Merge  

[Reason]  
- The PR correctly addresses the described issues with file modification detection and propagation. The changes are necessary and correct. The linter issues (cognitive complexity, public modifier in tests, Thread.sleep) are not correctness issues and should be ignored per the instructions.  

[Additional Notes]  
- None.