The changes in this PR have been added to the AWS SDK for Java v2 to handle cases where a file is modified during the read of the `FileAsyncRequestBody`.
    
    The changes are:
    
    1. The order of validation for file modifications - when reading bytes, once we have read the full file, we validate that the file has not been modified _before_ calling onNext on the subscription.  This ensures that the error is signaled before the subscriber (eg Netty) calls cancel.
    2. Change the exceptions signaled from the retryable IOException to a generic SdkClientException.
    3. Capture the `modifiedTimeAtStart` and `sizeAtStart` when the `FileAsyncRequestBody` is constructured, ensuring that it stays consistent between retries/splits.
    
    The tests have been added to cover the behavior of these changes.
    
    Manual testing of behavior:
    
    * Low-level clients:
    
      * S3AsyncClient: This behavior has been tested with both single and multi-part uploads using different HTTP clients (Netty and Crt). **No changes in behavior