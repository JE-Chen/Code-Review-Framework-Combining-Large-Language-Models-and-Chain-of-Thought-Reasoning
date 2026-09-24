This GitHub PR is for a bug fix in the AWS SDK for Java v2. The fix addresses three related issues:

1.  **Exceptions not propagated**: The PR ensures that exceptions signaled when a file is modified during a request are propagated to the subscriber (e.g., Netty).
2.  **IOExceptions are retryable**: The PR changes the exceptions signaled from IOExceptions to SdkClientExceptions, which are not retryable by default. This ensures that file modifications during a request are terminal.
3.  **File modifications between retries or parts not detected**: The PR captures the initial file modification time and size when the `FileAsyncRequestBody` is constructed, ensuring that these values stay consistent between retries or parts.

The PR includes the following modifications:

*   Changes the order of validation for file modifications: when reading bytes, the file is validated for changes before calling `onNext` on the subscription.
*   Changes the exceptions signaled from retryable IOExceptions to generic SdkClientExceptions.
*   Captures the `modifiedTimeAtStart` and `sizeAtStart` when the `FileAsyncRequestBody` is constructed, ensuring consistency between retries or parts.

The PR also includes new tests to cover the behavior and manual testing of the fix with different setups and