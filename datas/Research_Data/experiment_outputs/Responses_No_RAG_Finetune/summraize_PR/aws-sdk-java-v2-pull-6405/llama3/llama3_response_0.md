This GitHub PR addresses three related issues with the `FileAsyncRequestBody` class in the AWS SDK for Java v2:

1.  **Exceptions not propagated**: Exceptions signaled when file modifications are detected were not being propagated to the caller.
2.  **Retryable IOException**: The exceptions signaled were IOExceptions, which are considered retryable by default. However, file modifications during a request should be terminal.
3.  **File modifications between retries/splits not detected**: The file modification time and size were recorded when the `FileAsyncRequestBody` was constructed, but these values were not updated between retries or splits. As a result, file modifications between retries or splits were not detected.

The PR introduces three changes to address these issues:

1.  **Validation order changed**: The validation of file modifications is now done before calling `onNext` on the subscription. This ensures that errors are signaled before the subscriber (e.g., Netty) calls `cancel`.
2.  **Exception type changed**: The exceptions signaled are now generic `SdkClientException` instead of IOException, making it clear that the issue is not retryable.
3.  **File modification time and size captured**: The file modification time and size are now captured when the `FileAsyncRequestBody` is constructed