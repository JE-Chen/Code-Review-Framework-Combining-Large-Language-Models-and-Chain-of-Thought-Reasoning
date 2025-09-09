Here's a concise summary of the GitHub PR:

### **Core Problem**
The SDK silently ignored file modifications (size or last-modified time changes) during uploads, leading to:
1. **Unreported errors**: File modification exceptions were never surfaced to users.
2. **Retryable errors**: The thrown `IOException` was incorrectly marked as retryable (SDK would retry a terminal error).
3. **Undetected changes**: File metadata (size/mod time) was reset per upload part/retry, missing changes *between* retries/splits.

### **Key Fixes**
1. **Validation Timing**  
   Moved file modification checks **before** signaling the last bytes to the subscriber (Netty). Ensures errors are thrown *before* Netty cancels the subscription (per Reactive Streams spec).

2. **Non-Retryable Exception**  
   Changed `IOException` → `SdkClientException` (terminal error, not retried).

3. **Consistent Metadata**  
   Captured `modifiedTimeAtStart` and `sizeAtStart` **once at request start** (not per part/retry), ensuring all parts/splits use the same baseline.

### **User Impact**
- **Now fails fast** with a clear error when file changes are detected:  
  `SdkClientException: File last-modified time changed after reading started. Initial: 2025-09-05T19:20:46.540910708Z. Current: 2025-09-05T19:20:47.981202736Z`
- **Affects all non-CRT clients**:  
  `S3AsyncClient` (Netty), `S3CrtAsyncClient` (no change), `TransferManager` (Java/CRT).  
  *(CRT clients were unaffected as they handle file metadata differently.)*

### **Verification**
- Added 4 new tests covering:
  - File size changes (too short/long)
  - Last-modified time changes
  - Pre-set `modifiedTimeAtStart` (manual test)
  - Multi-part splits with mid-upload file changes
- All tests now throw `SdkClientException` (not `IOException`).

### **Why This Matters**
Prevents **silent data corruption** where uploads *succeed* but use a modified file (e.g., partial upload with stale file content). Users now get immediate, actionable errors.

> 💡 **Key Insight**: The fix ensures the SDK *never* continues a request after file changes are detected, eliminating a critical race condition.