This GitHub PR addresses three related issues with the `FileAsyncRequestBody` class:

1.  **Exceptions not propagated**: When file modifications are detected, exceptions are signaled as `IOExceptions`, which are retryable. However, these exceptions are not propagated to the caller.
2.  **Retryable exceptions**: The exceptions signaled are `IOExceptions`, which are considered retryable by default. However, file modifications during a request should be terminal.
3.  **File modifications between retries or parts not detected**: The `FileAsyncRequestBody` class records the initial modification time and file size when the publisher is created. However, if the file is modified between attempts or between parts, it is not detected.

The PR introduces three changes to address these issues:

1.  **Validation logic moved to `onComplete`**: The validation logic for file modifications is moved to the `onComplete` method, which is called after Netty cancels the subscription. This ensures that errors are signaled before the subscriber calls cancel.
2.  **Exceptions signaled as `SdkClientException`**: The exceptions signaled are changed from `IOException` to `SdkClientException`, which is not retryable.
3.  **Initial modification time and file size captured**: The initial modification time and file size