[Improvement Suggestions]  
No improvements needed.

[Meets Requirements]  
Yes

[Summary: Merge Decision]  
Merge

[Reason]  
The code correctly addresses all three issues described in the PR:  
1. File modification exceptions are now properly propagated by moving validation before `signalOnNext` (ensuring errors are signaled before Netty cancels the subscription).  
2. Exceptions are now `SdkClientException` (non-retryable) instead of `IOException`.  
3. `modifiedTimeAtStart` and `sizeAtStart` are consistently captured at construction time (not per subscription), ensuring detection across retries/splits.  
The test coverage has been updated to match the new exception type and behavior.

[Additional Notes]  
None.