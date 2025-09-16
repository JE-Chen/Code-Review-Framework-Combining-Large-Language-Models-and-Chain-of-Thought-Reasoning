**PR Summary**

This pull request addresses three related issues with the `FileAsyncRequestBody` class:

1. **Exceptions are not propagated**: When file modification is detected, an `IOException` is thrown, but it's not propagated to the caller. This PR changes the exception type to `SdkClientException` to ensure it's not retryable.
2. **File modifications are not detected**: The `FileAsyncRequestBody` class checks for file modifications only after the entire file has been read, which means errors are never signaled. This PR moves the validation logic to before calling `signalOnNext`, ensuring errors are signaled correctly.
3. **File modifications are not detected between retries or parts**: The `FileAsyncRequestBody` class records the initial file modification time and size when created, but it's not consistent between retries or parts. This PR captures the `modifiedTimeAtStart` and `sizeAtStart` when constructing the `FileAsyncRequestBody` instance.

**Modifications**

The PR makes three changes:

1. Changes the order of validation for file modifications to ensure errors are signaled before the subscriber (e.g., Netty) calls cancel.
2. Changes the exceptions signaled from `IOException` to `SdkClientException` to ensure it's not retryable.
3