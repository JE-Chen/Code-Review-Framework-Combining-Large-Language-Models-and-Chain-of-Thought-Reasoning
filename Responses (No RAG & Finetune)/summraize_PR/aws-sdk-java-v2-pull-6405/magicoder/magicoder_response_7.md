> I've made several changes to the `FileAsyncRequestBody` class to address the issues you've identified. Here's a summary of those changes:
    
    1. I've moved the validation of file modifications to the `onComplete` method, which is called after Netty cancels the subscription, ensuring the error is signaled before the subscriber calls `cancel`.
    
    2. I've changed the exceptions signaled from `IOException` to a more general `SdkClientException`.
    
    3. I've captured the `modifiedTimeAtStart` and `sizeAtStart` when the `FileAsyncRequestBody` is constructed, ensuring that it stays consistent between retries/splits.
    
    > I've also added tests to cover these changes. You can verify the new behavior by testing different scenarios involving file modifications for different parts of the SDK. Here are some examples:
    
    - Using the low-level clients:
    
      - S3AsyncClient (single/multi part, netty http client): This should throw a new exception.
      - S3AsyncClient (single/multi part, crt http