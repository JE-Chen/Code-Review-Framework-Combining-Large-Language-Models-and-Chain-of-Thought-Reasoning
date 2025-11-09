PR messages:
```
Surface errors from FileAsyncRequestBody when files are modified during request.

## Motivation and Context
This PR addresses three related issues:
1. Exceptions signaled when file modification are detected are not propagated.
2. Exceptions are IOExceptions which are retryable. 
3. File modifications between retry attempt or different parts (from split) are not detected.

We have logic in the [FileAsyncRequestBody](https://github.com/aws/aws-sdk-java-v2/blob/master/core/sdk-core/src/main/java/software/amazon/awssdk/core/internal/async/FileAsyncRequestBody.java#L409) that detected changes in file modification time and signaled IOExceptions - but these were not being propagated.
&nbsp;

The `NettyRequestExecutor` (which, indirectly, is subscribed to the `FileAsyncRequestBody.FilePublisher`) calls `cancel` when  Netty detects that it has read the full expected content-length (see logic [here](https://github.com/aws/aws-sdk-java-v2/blob/a4102def007a7b7a7e76efd30c7e07721dba25a1/http-clients/netty-nio-client/src/main/java/software/amazon/awssdk/http/nio/netty/internal/NettyRequestExecutor.java#L455)).  Once `cancel` has been called, the Reactive Streams spec specifies that errors should no longer be signaled (and our code respects that).  The check for file modification time changes is only done in `onComplete` which is only called after Netty cancels the subscription, meaning errors will never be signaled.    The solution to this is to move the validation logic into the onComplete during read, specifically a check [here](https://github.com/aws/aws-sdk-java-v2/blob/master/core/sdk-core/src/main/java/software/amazon/awssdk/core/internal/async/FileAsyncRequestBody.java#L341) *before* the call to `signalOnNext` (which will cause Netty to call cancel).

&nbsp;
The second issue is that the exception raised is an IOException, which is considered retryable by default.  File modification during request should be terminal. 

&nbsp;
The third issue is that we were recording the initial modification time and file size when the Publisher is created - which is done per execution attempt / per part in split, so if the file is modified between attempts or between parts, it was not being detected.

## Modifications
There are three changes, which address each of the issues listed above.

1. Change the order of validation for file modifications - when reading bytes, once we have read the full file, we validate that the file has not been modified *before* calling onNext on the subscription.  This ensures that the error is signaled before the subscriber (eg Netty) calls cancel. 
2. Change the exceptions signaled from the retryable IOException to a generic SdkClientException.
3. Capture the `modifiedTimeAtStart` and `sizeAtStart` when the `FileAsyncRequestBody` is constructured, ensuring that it stays consistent between retries/splits.

## Testing
Added new tests to cover behavior.

Manual testing of behavior:
**Behavior of putObject/uploadFile with different setups when file modified**:

Low level clients:
* S3AsyncClient (single/multi part, netty http client):  **Throws new exception**
* S3AsyncClient (single/multi part, crt http client) - **Throws new exception**
* S3CrtAsyncClient - **No Change in behavior** - No exception, request completes normally.

TransferManagers:
* Java TM (single/multi part): **Throws new exception**
* CrtTM: **No change in behavior** - no exception, completes normally.

Example exception:
```
software.amazon.awssdk.core.exception.SdkClientException: Unable to execute HTTP request: File last-modified time changed after reading started. Initial modification time: 2025-09-05T19:20:46.540910708Z. Current modification time: 2025-09-05T19: