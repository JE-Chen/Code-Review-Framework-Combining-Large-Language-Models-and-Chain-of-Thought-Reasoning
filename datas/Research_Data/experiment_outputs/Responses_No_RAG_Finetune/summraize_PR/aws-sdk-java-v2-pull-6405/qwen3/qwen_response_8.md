Here's a concise summary of the GitHub PR:

### **Core Problem**
File modification detection in `FileAsyncRequestBody` was broken, causing **unreported errors** when files changed during upload. Key issues:
1. **Errors not propagated**: Validation logic ran *after* Netty canceled the subscription (via `cancel()`), so exceptions never reached the caller.
2. **Retryable errors**: Threw `IOException` (retryable by default), but file changes should be **terminal errors**.
3. **State not preserved**: Initial file metadata (size/mod time) was re-captured per retry/split, missing modifications *between* attempts.

### **Key Fixes**
1. **Validation moved upstream**  
   - Checks file integrity **before** `onNext` (when Netty still accepts errors), ensuring errors are surfaced *before* cancellation.
2. **Non-retryable exception**  
   - Replaced `IOException` with `SdkClientException` (terminal error).
3. **Consistent metadata capture**  
   - Store `modifiedTimeAtStart` and `sizeAtStart` at **construction** (not per retry/split), enabling detection of modifications *across* retries/splits.

### **Verification**
- **Added tests** covering:
  - File size change during upload (too short/long).
  - File modification time change (before/after upload).
  - Split uploads (multi-part) with file changes mid-upload.
- **Manual tests** confirmed:
  - ✅ **S3AsyncClient** (Netty/CRT): Throws `SdkClientException`.
  - ❌ **S3CrtAsyncClient/TransferManager (CRT)**: Unchanged (no file checks).
- **Example exception**:  
  `SdkClientException: File last-modified time changed... Initial: 2025-09-05T19:20:46.540910708Z. Current: 2025-09-05T19:20:47.981202736Z`

### **Impact**
- **Fixes critical bug** for Netty-based clients (S3AsyncClient, Java TransferManager).
- **Prevents silent failures** where uploads complete with corrupted data.
- **No behavioral change** for CRT clients (consistent with existing behavior).

### **Summary**
> *Ensures file modification errors are surfaced as non-retryable `SdkClientException` before Netty cancels the subscription, with consistent metadata capture across retries/splits.*  

*(PR type: Bug fix | Changes: 3 key modifications + tests)*