Recommend Merge

The PR addresses three related issues:
1. Exceptions signaled when file modification are detected are not propagated.
2. Exceptions are IOExceptions which are retryable. 
3. File modifications between retry attempt or different parts (from split) are not detected.

The code change addresses all these issues by:
- Moving the validation logic into the onComplete during read, specifically a check before calling onNext on the subscription. 
- Changing the exceptions signaled from the retryable IOException to a generic SdkClientException.
- Capturing the `modifiedTimeAtStart` and `sizeAtStart` when the `FileAsyncRequestBody` is constructured, ensuring that it stays consistent between retries/splits.

The code change also has tests to cover the behavior.

The changes pass all the tests and the quality gate checks.

This PR is of sufficient quality to be merged into the main branch.