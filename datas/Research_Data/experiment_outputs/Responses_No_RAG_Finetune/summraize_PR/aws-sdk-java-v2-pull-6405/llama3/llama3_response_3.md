This is a GitHub pull request (PR) that addresses three related issues with the `FileAsyncRequestBody` class in the AWS SDK for Java v2.

**Motivation and Context**

The PR aims to fix the following issues:

1. Exceptions signaled when file modifications are detected are not propagated.
2. Exceptions are `IOExceptions`, which are retryable by default, but file modifications during a request should be terminal.
3. File modifications between retry attempts or different parts (from split) are not detected.

**Modifications**

The PR introduces three changes to address the above issues:

1. **Change the order of validation for file modifications**: When reading bytes, once all expected bytes have been read, the code now validates that the file has not been modified before calling `onNext` on the subscription. This ensures that the error is signaled before the subscriber (e.g., Netty) calls `cancel`.
2. **Change the exceptions signaled from `IOException` to a generic `SdkClientException`**: This ensures that file modification exceptions are not retryable by default.
3. **Capture the `modifiedTimeAtStart` and `sizeAtStart` when the `FileAsyncRequestBody` is constructed**: This ensures that the file's modification time and size are consistent between