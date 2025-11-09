> The issue is fixed by adding validation logic at the start of request. It's now verified if file was modified during request and if it was then it throws a `SdkClientException`.
    > 
    > This change was made in the method `validateFileUnchanged` in `FileAsyncRequestBody.java`. It checks if the file size or modification time has changed during the request and if it has changed then it throws a `SdkClientException`. 
    > 
    > A test case named `changingFile_fileGetsDeleted_failsBecauseDeleted` has been added to validate this behavior.

    This PR addresses the issue of exceptions from `FileAsyncRequestBody` when files are modified during the request. It adds a `validateFileUnchanged` method in `FileAsyncRequestBody` which checks if the file size or modification time has changed during the request. If it has, it throws a `SdkClientException`. The `changedFileGetsDeleted_failsBecauseDeleted` test case is added to validate the behavior of the change.