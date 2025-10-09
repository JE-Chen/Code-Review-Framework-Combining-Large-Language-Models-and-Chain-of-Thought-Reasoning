### Summary of GitHub PR: File Modification Error Propagation Fix

**Problem Addressed**:  
The SDK failed to properly detect and propagate errors when a file was modified *during* an async HTTP request (e.g., during S3 uploads). Existing checks for file modification time/size changes were not surfaced to the caller, leading to:
1. **Silent failures** (errors were never thrown).
2. **Retryable errors** (using `IOException`, which the SDK retries by default).
3. **Inconsistent detection** (checks were done *after* the request was complete, missing modifications between retries/splits).

**Key Fixes**:
1. **Validation Timing**:  
   Moved file modification checks to **before** the last chunk is delivered to the subscriber (in `completed()`), ensuring errors are signaled *before* Netty cancels the subscription (per Reactive Streams spec).

2. **Non-Retryable Exception**:  
   Replaced `IOException` with `SdkClientException` (terminal error, not retried).

3. **Consistent Initial State**:  
   Captures `modifiedTimeAtStart` and `sizeAtStart` at `FileAsyncRequestBody` construction (not per retry/split), ensuring consistent checks across retries/splits.

**Testing Results**:
- **S3AsyncClient (Netty/CRT)**: Throws `SdkClientException` on file modification (e.g., `File last-modified time changed...`).
- **TransferManager (Java/CRT)**: Throws `SdkClientException` on file modification.
- **CRT Clients (S3CrtAsyncClient/CrtTM)**: Unchanged (they didn’t have this issue).
- **New Tests Added**: Cover file size changes, modification time changes, and multi-part splits.

**Example Error**:
```java
SdkClientException: 
  "File last-modified time changed after reading started. 
   Initial modification time: 2025-09-05T19:20:46.540910708Z. 
   Current modification time: 2025-09-05T19:20:47.981202736Z"
```

**Impact**:  
Prevents data corruption by failing *immediately* when a file is modified mid-upload, with clear terminal errors (not retryable). Fixes silent failures in the SDK.

**PR Type**:  
Bug fix (non-breaking, adds explicit error handling for file modifications).  
**Changelog**: Added as a bugfix entry.  
**License**: Apache 2.0.  

> **Why this matters**: Without this fix, users might unknowingly upload corrupted data (e.g., if a file was modified during upload) or face repeated failed retries. This ensures the SDK fails fast with actionable error messages.