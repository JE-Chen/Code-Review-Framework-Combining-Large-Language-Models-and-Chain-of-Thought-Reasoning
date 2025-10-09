This is a GitHub pull request that addresses three related issues with the `FileAsyncRequestBody` class in the AWS SDK for Java v2. The issues are:

1. Exceptions signaled when file modification are detected are not propagated.
2. Exceptions are `IOExceptions` which are retryable.
3. File modifications between retry attempts or different parts (from split) are not detected.

The changes made in this pull request include:

1. Changing the order of validation for file modifications - when reading bytes, once we have read the full file, we validate that the file has not been modified before calling `onNext` on the subscription. This ensures that the error is signaled before the subscriber (e.g., Netty) calls `cancel`.
2. Changing the exceptions signaled from the retryable `IOException` to a generic `SdkClientException`.
3. Capturing the `modifiedTimeAtStart` and `sizeAtStart` when the `FileAsyncRequestBody` is constructed, ensuring that it stays consistent between retries/splits.

The pull request includes new tests to cover the behavior and manual testing of behavior with different setups when a file is modified. The expected behavior is that the `FileAsyncRequestBody` should throw a new exception when a file is modified during the request.

Here