[Improvement Suggestions]  
No improvements needed.

[Meets Requirements]  
Yes

[Summary: Merge Decision]  
Merge

[Reason]  
The code correctly addresses the three issues identified in the PR description: moving file validation to occur before signaling the last bytes (ensuring errors are propagated before Netty cancels the subscription), changing exceptions to `SdkClientException` (non-retryable), and properly capturing `modifiedTimeAtStart` and `sizeAtStart` to ensure consistency across retries/splits. The tests are appropriate and cover the new behavior. The code quality issues identified (cognitive complexity, test code modifiers, Thread.sleep usage) are not related to correctness and are acceptable for this PR.

[Additional Notes]  
None.