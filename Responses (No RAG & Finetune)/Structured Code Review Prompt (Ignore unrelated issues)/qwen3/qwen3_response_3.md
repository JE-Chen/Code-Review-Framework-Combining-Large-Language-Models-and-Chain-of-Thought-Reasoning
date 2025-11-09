[PR Summary]  
This PR fixes a bug where file modification errors in FileAsyncRequestBody were not being propagated correctly. It moves the file validation logic to before signaling the last bytes to the subscriber, changes the exception type to SdkClientException, and ensures the initial file state is captured consistently for retries and splits.

[Key Improvements]  
- Ensures file modification errors are propagated to the client before Netty cancels the subscription
- Changes exception type from IOException to SdkClientException to prevent retrying on file modification errors
- Captures initial file state (modified time and size) consistently for retries and splits

[Improvement Suggestions]  
- Make `modifiedTimeAtStart()` and `sizeAtStart()` methods package-private instead of public

[Meets Requirements]  
Yes

[Summary: Merge Decision]  
Merge

[Reason]  
The PR correctly fixes the file modification error propagation issue. The only issue is the unnecessary public visibility of the `modifiedTimeAtStart()` and `sizeAtStart()` methods, which should be package-private. The cognitive complexity warning is a code quality issue, not a correctness issue, and the Thread.sleep() usage in tests is necessary for reliable test execution.

[Additional Notes]  
The linter's cognitive complexity warning (issue 1) is a code quality issue that doesn't affect correctness, and the Thread.sleep() usage in tests (issues 3 and 5) is necessary for reliable test execution. The only actionable issue is making the two methods package-private.