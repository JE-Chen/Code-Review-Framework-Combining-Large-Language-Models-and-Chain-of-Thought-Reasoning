```
[PR Summary]
- This PR fixes issues with file modification exceptions in AsyncRequestBody#fromFile.

[Key Improvements]
- File modifications between retry attempt or different parts (from split) are now detected.
- Exceptions are now properly propagated.
- The exceptions signaled are now generic SdkClientException.

[Improvement Suggestions]
- Ensure that file modification exceptions in AsyncRequestBody#fromFile are properly propagated.
- Implement a new generic SdkClientException for file modification exceptions.
- Capture the `modifiedTimeAtStart` and `sizeAtStart` when the `FileAsyncRequestBody` is constructured.

[Meets Requirements]
- Yes, the code follows the given rules and has no special problems.

[Summary: Merge Decision]
- Merge.

[Reason]
- This PR fixes the identified issues and improves the codebase.

[Additional Notes]
- None.
```

To summarize, the PR fixes the issues related to file modification in the AsyncRequestBody#fromFile. It updates the exceptions to be generic SdkClientException and captures the `modifiedTimeAtStart` and `sizeAtStart` when the `FileAsyncRequestBody` is constructed.