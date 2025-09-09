As per the description, the PR modifies the behavior of `FileAsyncRequestBody` to properly signal errors when file modification is detected during read. The modifications include:

    1. The validation of the file modification time prior to calling `onNext`, ensuring that the error is signaled before the subscriber (eg Netty) calls `cancel`.
    2. Changing the exceptions raised from retryable `IOException` to a generic `SdkClientException`.
    3. Capturing the `modifiedTimeAtStart` and `sizeAtStart` when the `FileAsyncRequestBody` is constructed, ensuring that it remains consistent between retries/splits.
    
    The new tests cover the behavior for various setups when the file is modified. 

    Low level clients:

    * S3AsyncClient (single/multi part, netty http client) - Throws new exception
    * S3AsyncClient (single/multi part, crt http client) - Throws new exception
    * S3CrtAsyncClient - No Change in behavior - No exception, request completes normally.

    TransferManagers:

    * Java