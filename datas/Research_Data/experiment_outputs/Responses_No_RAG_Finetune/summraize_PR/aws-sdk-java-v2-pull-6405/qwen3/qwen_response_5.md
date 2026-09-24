Here's a concise summary of the GitHub PR:

**Problem Addressed**:  
The SDK failed to properly handle file modifications during uploads (e.g., while an S3 `putObject` request was in progress). Existing logic checked for file changes but only in `onComplete` (after Netty had already canceled the subscription), so errors were never propagated. Additionally, the error was an `IOException` (retryable by default), but file modifications should be terminal (non-retryable).

**Key Fixes**:
1. **Propagate Errors Correctly**:  
   Moved file modification validation to occur *before* the last bytes are delivered to the subscriber (in `completed()`), ensuring errors are signaled *before* Netty cancels the subscription.

2. **Non-Retryable Exception**:  
   Changed the error type from `IOException` to `SdkClientException` (terminal, non-retryable).

3. **Consistent File Metadata**:  
   Captured `modifiedTimeAtStart` and `sizeAtStart` at `FileAsyncRequestBody` construction (not per retry/split), ensuring consistent checks across retries and split parts.

**Testing Results**:
- **All affected clients** (S3AsyncClient, TransferManager) now throw `SdkClientException` when file is modified during upload (e.g., `File last-modified time changed after reading started...`).
- **CRT clients** (S3CrtAsyncClient, CrtTM) unchanged (they already handled this correctly).
- New tests cover single/multi-part uploads, file size changes, and modification time mismatches.

**Impact**:  
- Fixes silent failures when files are modified during uploads.
- Ensures users get immediate, non-retryable errors instead of stuck requests.
- Maintains compatibility (no public API changes).

**Example Exception**:
```java
SdkClientException: 
  Unable to execute HTTP request: 
  File last-modified time changed after reading started. 
  Initial modification time: 2025-09-05T19:20:46.540910708Z. 
  Current modification time: 2025-09-05T19:20:47.981202736Z
```

**Summary**:  
This bug fix ensures file modification errors are **immediately surfaced as non-retryable exceptions**, preventing silent failures during uploads. All relevant clients (Netty-based) now behave consistently with CRT clients.