Here's a concise summary of the GitHub PR:

---

### **Core Problem**
The SDK failed to surface **file modification errors** during async file uploads (e.g., when a file was edited mid-upload). Instead, it silently ignored these errors or treated them as retryable `IOExceptions` (which they shouldn't be).

### **Key Issues Fixed**
1. **Errors not propagated**  
   - Validation logic (checking file modification time) was only run in `onComplete`, but Netty would cancel the subscription *before* `onComplete` was called. Errors were never surfaced to the user.

2. **Retryable exception type**  
   - The error was an `IOException` (treated as retryable by default), but file modifications should be **terminal** (non-retryable).

3. **Missing detection between retries/splits**  
   - File state (`modifiedTime`, `size`) was captured *per request attempt*, so modifications *between* retries or split parts went undetected.

---

### **Solution**
1. **Validation timing**  
   - Moved file modification checks **before** signaling `onNext` (ensuring errors are raised *before* Netty cancels the subscription).

2. **Non-retryable exception**  
   - Replaced `IOException` with `SdkClientException` (terminal error, not retryable).

3. **Stable file state**  
   - Captured `modifiedTimeAtStart` and `sizeAtStart` **once at construction** (not per retry/split), ensuring consistent validation across all parts.

---

### **Behavior Change**
- **Before**: Silent failure or retryable `IOException` (e.g., `File size changed after reading started` as a retryable error).
- **After**: Immediate `SdkClientException` (non-retryable) with clear details:
  ```java
  SdkClientException: File last-modified time changed after reading started. 
  Initial modification time: 2025-09-05T19:20:46.540910708Z. 
  Current modification time: 2025-09-05T19:20:47.981202736Z
  ```

---

### **Testing & Coverage**
- Added tests for:
  - File modification during upload (single/multi-part).
  - Preset `modifiedTimeAtStart` (to validate state capture).
  - Split uploads (e.g., multipart with file changed between parts).
- Verified **all non-CRT clients** (S3AsyncClient, TransferManager) now throw the new exception.
- **CRT clients unchanged** (they already handled this correctly).

---

### **Why It Matters**
- Users **no longer get silent failures** when a file is modified mid-upload.
- Errors are **explicitly non-retryable**, preventing wasted retries.
- Fixes a critical edge case in multi-part uploads (e.g., S3 uploads where a file is edited between parts).

> ✅ **Type**: Bug fix (non-breaking, resolves silent failures).  
> ✅ **Impact**: Critical for reliability in file uploads.  
> ✅ **Changelog**: `Ensure that file modification exceptions in FileAsyncRequestBody are propagated correctly.`

---

**In short**: The SDK now **immediately fails with a clear error** if a file is modified during an async upload, preventing silent data corruption and unnecessary retries.