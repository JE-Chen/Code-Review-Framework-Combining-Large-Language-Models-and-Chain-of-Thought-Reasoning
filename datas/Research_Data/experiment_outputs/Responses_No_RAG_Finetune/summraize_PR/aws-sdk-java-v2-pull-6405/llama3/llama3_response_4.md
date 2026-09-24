This GitHub PR addresses three related issues with the `FileAsyncRequestBody` class in the AWS SDK for Java v2:

1.  **Exceptions not propagated**: When a file is modified during a request, the exceptions signaled by the `FileAsyncRequestBody` were not being propagated to the caller.
2.  **IOExceptions are retryable**: The exceptions signaled by the `FileAsyncRequestBody` were `IOExceptions`, which are considered retryable by default. However, file modifications during a request should be terminal.
3.  **File modifications not detected**: The `FileAsyncRequestBody` was recording the initial modification time and file size when the publisher was created, but this was done per execution attempt or per part in a split. As a result, if the file was modified between attempts or between parts, it was not being detected.

The PR makes three changes to address these issues:

1.  **Validation order changed**: When reading bytes from the file, the validation for file modifications is now done before calling `onNext` on the subscription. This ensures that the error is signaled before the subscriber (e.g., Netty) calls `cancel`.
2.  **Exception type changed**: The exceptions signaled by the `FileAsyncRequestBody` are now `SdkClientException