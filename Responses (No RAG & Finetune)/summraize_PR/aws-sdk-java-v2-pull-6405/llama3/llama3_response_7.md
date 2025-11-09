This GitHub PR aims to address three related issues with the `FileAsyncRequestBody` class in the AWS SDK for Java v2.

**Motivation and Context**

The issues are:

1. Exceptions signaled when file modifications are detected are not propagated.
2. Exceptions are IOExceptions, which are retryable.
3. File modifications between retry attempts or different parts (from split) are not detected.

**Modifications**

The PR introduces three changes to address these issues:

1. **Validation order change**: The validation logic for file modifications is moved to the `onComplete` method, which is called after reading the full expected content-length. This ensures that errors are signaled before the subscriber (e.g., Netty) calls cancel.
2. **Exception type change**: The exceptions signaled are changed from IOExceptions to generic SdkClientExceptions, which are not retryable.
3. **Initial file status capture**: The initial file modification time and size are captured when the `FileAsyncRequestBody` is constructed, ensuring consistency between retries/splits.

**Testing**

The PR adds new tests to cover the behavior of `FileAsyncRequestBody` in various scenarios, including:

* File modification during reading
* File deletion during reading
* File size change during reading
* File modification between retry