[PR Summary]  
- This PR addresses three related issues in the FileAsyncRequestBody class:
  1. Exceptions signaled when file modification are detected are not propagated.
  2. Exceptions are IOExceptions which are retryable.
  3. File modifications between retry attempt or different parts (from split) are not detected.
- The PR includes three changes to address these issues:
  1. Change the order of validation for file modifications - when reading bytes, once we have read the full file, we validate that the file has not been modified *before* calling onNext on the subscription.
  2. Change the exceptions signaled from the retryable IOException to a generic SdkClientException.
  3. Capture the `modifiedTimeAtStart` and `sizeAtStart` when the `FileAsyncRequestBody` is constructed, ensuring that it stays consistent between retries/splits.

[Key Improvements]  
- Propagate file modification exceptions correctly.
- Change the exceptions signaled from retryable IOException to a generic SdkClientException.
- Detect file modifications between retry attempts or different parts (from split).

[Improvement Suggestions]  
- Consider refactoring the validateFileUnchangedAndSignalErrors method to reduce its Cognitive Complexity from 21 to 15.
- Remove unnecessary 'public' modifiers in test code.

[Meets Requirements]  
- Yes

[Summary: Merge Decision]  
- Merge

[Reason]  
- The PR addresses the specified issues and includes necessary changes to fix them.