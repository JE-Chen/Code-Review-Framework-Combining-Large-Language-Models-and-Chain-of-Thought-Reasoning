Here's a concise summary of the GitHub PR:

**Problem:**  
File modification during an upload (e.g., while S3 is reading the file) would go undetected in the AWS SDK for Java v2. Errors were silently swallowed because validation logic ran *after* Netty canceled the subscription (per Reactive Streams spec), making the error non-retryable and unobservable to the user. File metadata checks were also inconsistent across retries/splits.

**Fix:**  
1. **Validation Timing:** Moved file modification checks to occur *before* sending the last bytes to the subscriber (Netty), ensuring errors are propagated *before* cancellation.  
2. **Error Type:** Changed from `IOException` (retryable) to `SdkClientException` (terminal, non-retryable).  
3. **Metadata Consistency:** Captured file `modifiedTime` and `size` at `FileAsyncRequestBody` construction (not per-request) to ensure consistent checks across retries/splits.  

**Impact:**  
- **Now throws clear terminal exceptions** (e.g., `File last-modified time changed after reading started`).  
- **Fixes behavior for all non-CRT clients** (S3AsyncClient, TransferManager), while CRT clients remain unaffected (as they use different file handling).  
- **Added tests** cover all edge cases (file size change, modification time change, deletion, split uploads).  

**Key Change:**  
The error is now properly surfaced *before* Netty cancels the subscription, making file modification a terminal error (not silently ignored).  

**Changelog Entry:**  
> `Bug fix: Ensure file modification exceptions in FileAsyncRequestBody are propagated correctly.`  

*(This PR is a critical bug fix for upload reliability, ensuring users are notified when files are modified mid-upload.)*