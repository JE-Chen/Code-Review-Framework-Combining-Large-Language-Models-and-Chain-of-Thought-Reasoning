This GitHub PR is a bug fix that addresses three related issues with the `FileAsyncRequestBody` class in the AWS SDK for Java v2. The issues are:

1. **Exceptions not propagated**: When a file is modified during a request, exceptions are signaled, but they are not propagated to the caller.
2. **Retryable exceptions**: The exceptions signaled when a file is modified are `IOExceptions`, which are considered retryable by default. However, file modifications during a request should be terminal.
3. **File modifications not detected**: The code was recording the initial modification time and file size when the publisher is created, but this was done per execution attempt or per part in a split. As a result, if the file was modified between attempts or between parts, it was not being detected.

To address these issues, the PR makes three changes:

1. **Change the order of validation**: When reading bytes, the code now validates that the file has not been modified before calling `onNext` on the subscription. This ensures that the error is signaled before the subscriber (e.g., Netty) calls `cancel`.
2. **Change the exceptions signaled**: The exceptions signaled when a file is modified are now `SdkClientException`s, which are not retryable