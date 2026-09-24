This is a GitHub pull request (PR) that addresses three related issues with the AWS SDK for Java v2's `FileAsyncRequestBody` class:

**Motivation and Context**

The PR aims to fix three issues:

1. Exceptions signaled when file modifications are detected are not propagated.
2. Exceptions are IOExceptions, which are retryable.
3. File modifications between retry attempts or different parts (from split) are not detected.

**Modifications**

The PR introduces three changes to address the issues:

1. **Change the order of validation for file modifications**: When reading bytes, the file is validated for modifications before calling `onNext` on the subscription. This ensures that errors are signaled before the subscriber (e.g., Netty) calls cancel.
2. **Change the exceptions signaled from IOException to SdkClientException**: The exceptions are changed from IOException to SdkClientException, which is not retryable.
3. **Capture the modified time and size at the start of the request**: The modified time and size of the file are captured when the `FileAsyncRequestBody` is constructed, ensuring consistency between retries/splits.

**Testing**

The PR adds new tests to cover the behavior, including:

* Testing that file modifications are detected and signaled as an exception.
