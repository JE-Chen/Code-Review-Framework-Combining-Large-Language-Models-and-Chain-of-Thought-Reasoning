Based on the provided PR, I recommend merging it into the main branch.

The changes address three related issues:

1. Exceptions signaled when file modification are detected are not propagated.
2. Exceptions are IOExceptions which are retryable.
3. File modifications between retry attempt or different parts (from split) are not detected.

The modifications include:

1. Changing the order of validation for file modifications - when reading bytes, once we have read the full file, we validate that the file has not been modified *before* calling onNext on the subscription.
2. Changing the exceptions signaled from the retryable IOException to a generic SdkClientException.
3. Capturing the `modifiedTimeAtStart` and `sizeAtStart` when the `FileAsyncRequestBody` is constructed, ensuring that it stays consistent between retries/splits.

The code changes are well-structured and follow the coding conventions of the project. The tests are comprehensive and cover various scenarios.

The issues reported by SonarQube are minor and do not impact the overall quality of the code. Issue1 is a minor refactoring issue that can be addressed later. Issue2 is a style issue that can be fixed by removing the public modifier. Issue3 is a good practice issue that can be addressed by using a more robust testing approach.

Overall, the PR is well-written, and the changes are necessary to fix the issues mentioned in the PR description. Therefore, I recommend merging it into the main branch.

Improvement Suggestions:

1. Refactor the `validateFileUnchangedAndSignalErrors()` method to reduce its Cognitive Complexity.
2. Remove the public modifier from the test class and methods.
3. Replace `Thread.sleep()` with a more robust testing approach, such as using a timer or a mock clock.

Recommendation: Merge